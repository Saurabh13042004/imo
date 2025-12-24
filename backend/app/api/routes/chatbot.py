"""Chatbot API routes for product Q&A using Gemini AI."""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import google.generativeai as genai

from app.config import settings
from app.api.dependencies import get_optional_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])

# Initialize Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    logger.warning("GEMINI_API_KEY not configured - chatbot will not work")
    model = None


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chatbot."""
    message: str = Field(..., description="User's message")
    product_title: str = Field(..., description="Product title")
    product_description: Optional[str] = Field(None, description="Product description")
    product_price: Optional[str] = Field(None, description="Product price")
    product_rating: Optional[float] = Field(None, description="Product rating")
    product_reviews_count: Optional[int] = Field(None, description="Number of reviews")
    ai_verdict: Optional[dict] = Field(None, description="AI verdict data")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous messages")


class ChatResponse(BaseModel):
    """Response model for chatbot."""
    message: str = Field(..., description="AI assistant's response")
    error: Optional[str] = Field(None, description="Error message if any")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_product(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Chat with AI assistant about a product.
    
    Uses Gemini AI to answer questions about the product based on:
    - Product details (title, description, price, rating)
    - AI verdict (pros, cons, summary)
    - Conversation history for context
    """
    if not model:
        raise HTTPException(
            status_code=503,
            detail="AI chatbot service is not available. Please configure GEMINI_API_KEY."
        )
    
    try:
        # Build context about the product
        product_context = f"""Product Information:
Title: {request.product_title}
"""
        
        if request.product_description:
            product_context += f"Description: {request.product_description}\n"
        
        if request.product_price:
            product_context += f"Price: {request.product_price}\n"
        
        if request.product_rating:
            product_context += f"Rating: {request.product_rating}/5"
            if request.product_reviews_count:
                product_context += f" ({request.product_reviews_count} reviews)"
            product_context += "\n"
        
        # Add AI verdict if available
        if request.ai_verdict:
            product_context += "\nAI Analysis:\n"
            if request.ai_verdict.get("summary"):
                product_context += f"Summary: {request.ai_verdict['summary']}\n"
            
            if request.ai_verdict.get("pros"):
                pros = request.ai_verdict["pros"]
                if isinstance(pros, list):
                    product_context += f"Pros: {', '.join(pros)}\n"
                else:
                    product_context += f"Pros: {pros}\n"
            
            if request.ai_verdict.get("cons"):
                cons = request.ai_verdict["cons"]
                if isinstance(cons, list):
                    product_context += f"Cons: {', '.join(cons)}\n"
                else:
                    product_context += f"Cons: {cons}\n"
            
            if request.ai_verdict.get("imo_score"):
                product_context += f"IMO Score: {request.ai_verdict['imo_score']}/100\n"
        
        # Build conversation history
        conversation = []
        for msg in request.conversation_history[-5:]:  # Keep last 5 messages for context
            conversation.append(f"{msg.role.upper()}: {msg.content}")
        
        conversation_context = "\n".join(conversation) if conversation else "No previous conversation."
        
        # Create the prompt
        system_prompt = """You are IMO AI, a friendly and knowledgeable shopping assistant helping users make informed purchase decisions.

Your role:
- Answer questions about the product based on the provided information
- Be helpful, concise, and conversational
- Use emojis occasionally to be friendly but not excessive
- If asked about features not mentioned in the product info, be honest that you don't have that specific detail
- Focus on helping the user decide if this product is right for them
- Reference the AI analysis (pros, cons, score) when relevant
- Keep responses under 150 words unless a detailed answer is needed

Remember:
- You're analyzing THIS specific product based on the data provided
- Be objective and honest about both positives and negatives
- If the user asks about alternatives or comparisons, suggest they can search for other products
- Format your responses nicely with bullet points or short paragraphs for readability
"""
        
        user_prompt = f"""{system_prompt}

{product_context}

Previous Conversation:
{conversation_context}

User's Question: {request.message}

Please provide a helpful, friendly response:"""
        
        # Call Gemini API
        logger.info(f"[Chatbot] Processing question about '{request.product_title}': {request.message[:50]}...")
        
        response = model.generate_content(
            user_prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 500,
            }
        )
        
        ai_message = response.text.strip()
        logger.info(f"[Chatbot] Generated response: {ai_message[:100]}...")
        
        return ChatResponse(message=ai_message)
    
    except Exception as e:
        logger.error(f"[Chatbot] Error generating response: {e}", exc_info=True)
        return ChatResponse(
            message="I'm having trouble processing your question right now. Please try again in a moment.",
            error=str(e)
        )
