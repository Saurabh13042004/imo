/**
 * Demo product data for featured products detail pages
 * This provides complete product information including enriched data, reviews, AI verdicts, and store pricing
 */

import { Thumb } from "@radix-ui/react-slider";

export const DEMO_PRODUCTS = {
  fp1: {
    // Product Basic Info
    id: "fp1",
    title: "Premium Wireless Headphones",
    description: "High-quality wireless headphones with active noise cancellation and premium sound quality.",
    price: 199.99,
    image_url: "https://image.cdn.shpy.in/305289/SKU-1621_0-1730988839304.webp?width=600&format=webp",
    product_url: "https://www.amazon.com/gp/product/B09XXXXXXXXX",
    source: "Amazon",
    source_id: null,
    imo_score: 9.2,
    site_rating: 4.8,
    reviews_count: 2450,
    like_count: 342,
    liked_by_user: false,
    created_at: new Date().toISOString(),
    pros: [
      "Excellent sound quality",
      "30-hour battery life",
      "Comfortable fit for extended wear",
      "Active noise cancellation",
      "Touch controls"
    ],
    cons: [
      "Premium price point",
      "Limited color options",
      "Slightly heavy"
    ],
    image_urls: [
      "https://image.cdn.shpy.in/305289/SKU-1621_0-1730988839304.webp?width=600&format=webp",
      "https://m.media-amazon.com/images/I/71O2e8YM-nL._AC_SX679_.jpg",
      "https://m.media-amazon.com/images/I/61OMvbVBsNL._AC_SX679_.jpg"
    ],
    brand: "AudioTech Pro",
    specifications: {
      "Driver Size": "40mm",
      "Frequency Response": "20Hz - 20kHz",
      "Impedance": "32 Ohms",
      "Battery Life": "Up to 30 hours",
      "Charging Time": "2 hours via USB-C",
      "Bluetooth Version": "5.3",
      "Weight": "250g",
      "Warranty": "2 years",
      "Colors Available": "Black, Silver, Midnight Blue",
      "Water Resistance": "IPX4"
    },
    enrichedData: {
      description: "Professional-grade wireless headphones featuring adaptive noise cancellation, 30-hour battery life, and premium audio drivers. Perfect for music enthusiasts and professionals who demand superior sound quality.",
      amazon_reviews: [
        {
          id: "R1",
          author: "Sarah M.",
          rating: 5,
          title: "Best headphones I've ever owned!",
          content: "The sound quality is absolutely amazing. The noise cancellation works incredibly well, and the battery lasts forever. Highly recommend for anyone looking for premium headphones.",
          is_verified: true,
          helpful_count: 234,
          timestamp: "2024-12-10"
        },
        {
          id: "R2",
          author: "John D.",
          rating: 4,
          title: "Great quality, a bit pricey",
          content: "Sound quality is top-notch and they're very comfortable. My only complaint is the price, but they're definitely worth it if you use headphones daily.",
          is_verified: true,
          helpful_count: 156,
          timestamp: "2024-11-28"
        }
      ],
      external_reviews: [
        {
          id: "E1",
          author: "TechReview Central",
          rating: 4.5,
          title: "Best wireless headphones of 2024",
          content: "After testing over 50 models, these rank among the absolute best for audio quality and comfort.",
          source: "TechReview Central"
        }
      ],
      immersive_data: {
        product_results: {
          title: "Premium Wireless Headphones",
          user_reviews: [
            {
              text: "Absolutely love these headphones. Crystal clear sound and incredibly comfortable to wear all day.",
              source: "walmart.com",
              rating: 5,
              date: "2024-12-15T00:00:00Z",
              user_name: "Mike R."
            },
            {
              text: "Great product but took 3 weeks to arrive. Otherwise very happy with my purchase.",
              source: "bestbuy.com",
              rating: 4,
              date: "2024-12-08T00:00:00Z",
              user_name: "Emma L."
            }
          ],
          videos: [
            {
              title: "Premium Wireless Headphones - Full Review",
              description: "Comprehensive review of the Premium Wireless Headphones",
              link: "https://www.youtube.com/watch?v=zZlYnk6BvBs",
              thumbnail: "https://img.youtube.com/vi/zZlYnk6BvBs/mqdefault.jpg"
            },

            {
              title: "Unboxing and First Impressions",
              description: "Unboxing the Premium Wireless Headphones and sharing first impressions",
              link: "https://www.youtube.com/watch?v=tIHldrPlsTk",
              thumbnail: "https://img.youtube.com/vi/tIHldrPlsTk/mqdefault.jpg"
            },

            {
              title: "Top 5 Features of Premium Wireless Headphones",
              description: "Highlighting the top 5 features of the Premium Wireless Headphones",
              link: "https://www.youtube.com/watch?v=JFfPF9r8Ueg",
              thumbnail: "https://img.youtube.com/vi/JFfPF9r8Ueg/mqdefault.jpg"
            },

            {
              title: "How to Maximize Battery Life",
              description: "Tips and tricks to get the most out of your Premium Wireless Headphones' battery life",
              link: "https://www.youtube.com/watch?v=N3UmLVLVdXk",
              thumbnail: "https://img.youtube.com/vi/N3UmLVLVdXk/mqdefault.jpg"
            }
          ],
          short_videos: [
            {
              title: "Quick Look at Premium Wireless Headphones",
              link: "https://www.youtube.com/watch?v=QeX5j3Yz1jM",
              thumbnail: "https://img.youtube.com/vi/QeX5j3Yz1jM/mqdefault.jpg"
            },
            {
              title: "Premium Wireless Headphones Sound Test",
              link: "https://www.youtube.com/watch?v=V7bX9F3K2jY",
              thumbnail: "https://img.youtube.com/vi/V7bX9F3K2jY/mqdefault.jpg"
            },

            {
              title: "Setting Up Your Premium Wireless Headphones",
              link: "https://www.youtube.com/watch?v=Hk3J9L4m8QY",
              thumbnail: "https://img.youtube.com/vi/Hk3J9L4m8QY/mqdefault.jpg"

            },

            {
              title: "Premium Wireless Headphones vs Competitors",
              link: "https://www.youtube.com/watch?v=Gz2L8J9K3mE",
              thumbnail: "https://img.youtube.com/vi/Gz2L8J9K3mE/mqdefault.jpg"
            }



          ],

          stores: [
            {
              name: "Amazon",
              price: "$199.99",
              extracted_price: 199.99,
              link: "https://www.amazon.com",
              rating: 4.8,
              reviews: 2450,
              tag: "Popular Choice",
              details_and_offers: [
                "Free shipping on orders over $25",
                "Prime eligible - Free 2-day shipping",
                "30-day returns"
              ],
              delivery_details: [
                { type: "Free 2-day delivery" },
                { type: "In stock - Ships today" }
              ]
            },
            {
              name: "Best Buy",
              price: "$199.99",
              extracted_price: 199.99,
              link: "https://www.bestbuy.com",
              rating: 4.7,
              reviews: 1820,
              details_and_offers: [
                "Free in-store pickup available",
                "15% off for members",
                "Best Buy Protection Plan available"
              ],
              delivery_details: [
                { type: "Free same-day delivery" },
                { type: "Ready for pickup today" }
              ]
            },
            {
              name: "Walmart",
              price: "$189.99",
              extracted_price: 189.99,
              link: "https://www.walmart.com",
              rating: 4.6,
              reviews: 1205,
              tag: "Best Price",
              details_and_offers: [
                "Free 2-day shipping on $35+ orders",
                "Price match guarantee",
                "Easy returns at any Walmart"
              ],
              delivery_details: [
                { type: "Free shipping on $35+" },
                { type: "Ships in 1-2 business days" }
              ]
            }
          ],
          about_the_product: {
            description: "Professional-grade wireless headphones featuring adaptive noise cancellation, 30-hour battery life, and premium audio drivers. Perfect for music enthusiasts and professionals who demand superior sound quality.",
            features: [
              { title: "Driver Size", value: "40mm" },
              { title: "Frequency Response", value: "20Hz - 20kHz" },
              { title: "Impedance", value: "32 Ohms" },
              { title: "Battery Life", value: "Up to 30 hours" },
              { title: "Charging Time", value: "2 hours via USB-C" },
              { title: "Bluetooth Version", value: "5.3" },
              { title: "Weight", value: "250g" },
              { title: "Water Resistance", value: "IPX4" }
            ]
          },
          ratings: [
            { stars: 5, amount: 1200 },
            { stars: 4, amount: 800 },
            { stars: 3, amount: 300 },
            { stars: 2, amount: 100 },
            { stars: 1, amount: 50 }
          ]
        }
      }
    },
    aiVerdict: {
      verdict_score: 9.2,
      summary: "Premium wireless headphones that deliver exceptional audio quality and comfort. Highly recommended for daily use and professional applications.",
      detailed_analysis: "These headphones represent the pinnacle of consumer audio technology, combining premium build quality with advanced features. The 30-hour battery life eliminates frequent charging hassles, while the adaptive noise cancellation performs as well as or better than many competitors at twice the price.",
      pros: [
        "Superior audio quality with rich bass and clear treble",
        "Exceptional 30-hour battery life",
        "Effective active noise cancellation",
        "Comfortable fit even after extended wear",
        "Excellent touch controls and intuitive interface",
        "Premium build quality with premium materials"
      ],
      cons: [
        "Premium price point compared to alternatives",
        "Limited color variations available",
        "Slightly heavier than some competitors",
        "Proprietary audio codec not universally supported"
      ],
      who_should_buy: [
        "Audiophiles and music enthusiasts",
        "Professionals who need reliable audio equipment",
        "Travelers and commuters",
        "Remote workers and students",
        "Content creators and podcasters"
      ],
      who_should_avoid: [
        "Budget-conscious buyers",
        "Users who prefer lighter headphones",
        "Those who need wireless charging"
      ],
      deal_breakers: [],
      best_for: "Anyone seeking premium wireless headphones with outstanding audio quality, battery life, and reliability",
      comparison: "Comparable to Bose QuietComfort and Sony WH-1000XM5, but at a better price point"
    }
  },
  fp2: {
    // Product Basic Info
    id: "fp2",
    title: "4K Ultra HD Monitor",
    description: "27-inch 4K monitor perfect for professionals and gamers with USB-C connectivity.",
    price: 449.99,
    image_url: "https://www.lg.com/content/dam/channelbtb/lgcom/in/images/business/24ud58-b_atr_eail_in_b/gallery/24UD58-B-DZ-01.jpg",
    product_url: "https://www.walmart.com/gp/product/B09XXXXXXXXX",
    source: "Walmart",
    source_id: null,
    imo_score: 8.9,
    site_rating: 4.6,
    reviews_count: 1820,
    like_count: 267,
    liked_by_user: false,
    created_at: new Date().toISOString(),
    pros: [
      "Sharp 4K display",
      "USB-C connectivity",
      "Adjustable stand",
      "Color accurate",
      "Low latency"
    ],
    cons: [
      "Can get warm under load",
      "Expensive",
      "Limited speaker quality"
    ],
    image_urls: [
      "https://www.lg.com/content/dam/channelbtb/lgcom/in/images/business/24ud58-b_atr_eail_in_b/gallery/24UD58-B-DZ-01.jpg",
      "https://images-na.ssl-images-amazon.com/images/I/91Q6Y1qiC2L._AC_SL1500_.jpg",
      "https://images-na.ssl-images-amazon.com/images/I/81wB7jTLGGL._AC_SL1500_.jpg"
    ],
    brand: "LG Professional",
    specifications: {
      "Screen Size": "27 inches",
      "Resolution": "3840 x 2160 (4K UHD)",
      "Panel Type": "IPS",
      "Refresh Rate": "60Hz",
      "Response Time": "5ms (gray-to-gray)",
      "Color Gamut": "99% Adobe RGB",
      "Brightness": "350 nits",
      "Contrast Ratio": "1000:1",
      "Inputs": "USB-C (with power delivery), HDMI x2, DisplayPort",
      "Warranty": "3 years",
      "Adjustability": "Height, Tilt, Swivel, Pivot",
      "Weight": "8.2 kg"
    },
    enrichedData: {
      description: "Professional-grade 27-inch 4K monitor featuring USB-C connectivity, HDR support, and factory-calibrated color accuracy. Ideal for content creators, video editors, and gamers seeking pristine image quality.",
      amazon_reviews: [
        {
          id: "R1",
          author: "David T.",
          rating: 5,
          title: "Perfect monitor for content creation",
          content: "The color accuracy is exceptional. I use this for video editing and color grading, and it never disappoints. The USB-C connectivity is a nice bonus.",
          is_verified: true,
          helpful_count: 189,
          timestamp: "2024-12-12"
        },
        {
          id: "R2",
          author: "Lisa K.",
          rating: 4,
          title: "Great monitor, runs hot",
          content: "Excellent display quality and the USB-C is very convenient. My only concern is that it gets quite warm during extended use. Make sure you have good ventilation.",
          is_verified: true,
          helpful_count: 142,
          timestamp: "2024-12-01"
        }
      ],
      external_reviews: [
        {
          id: "E1",
          author: "ProDisplay Reviews",
          rating: 4.5,
          title: "Best 4K monitor for professionals in 2024",
          content: "Exceptional color accuracy and build quality make this one of the best professional monitors available.",
          source: "ProDisplay Reviews"
        }
      ],
      immersive_data: {
        product_results: {
          title: "4K Ultra HD Monitor",
          user_reviews: [
            {
              text: "Amazing display quality. Perfect for my photo editing work. The USB-C is super convenient.",
              source: "bestbuy.com",
              rating: 5,
              date: "2024-12-14T00:00:00Z",
              user_name: "Photography Pro"
            },
            {
              text: "Great monitor but pricey. The heat issue is real though, make sure your desk setup has good airflow.",
              source: "walmart.com",
              rating: 4,
              date: "2024-12-09T00:00:00Z",
              user_name: "Tech Reviewer"
            }
          ],
          videos: [
            {
              title: "4K Monitor Professional Setup & Review",
              description: "Complete review of professional 4K monitors for content creators",
              link: "https://www.youtube.com/watch?v=FlLMxRjdATM",
              thumbnail: "https://img.youtube.com/vi/FlLMxRjdATM/mqdefault.jpg"
            },
            {
              title: "4K Ultra HD Monitor - Unboxing & First Impressions",
              description: "Unboxing and initial setup of the 4K Ultra HD Monitor",
              link: "https://www.youtube.com/watch?v=0JcY3mB6aCw",
              thumbnail: "https://img.youtube.com/vi/0JcY3mB6aCw/mqdefault.jpg"
            },
            {
              title: "Best 4K Monitor for Video Editing",
              description: "In-depth look at color accuracy and video editing capabilities",
              link: "https://www.youtube.com/watch?v=S9xfTk-hVT4",
              thumbnail: "https://img.youtube.com/vi/S9xfTk-hVT4/mqdefault.jpg"
            },
            {
              title: "4K Monitor Gaming Performance & Features",
              description: "Testing gaming performance and advanced features on 4K display",
              link: "https://www.youtube.com/watch?v=dj5s5PsAeMw",
              thumbnail: "https://img.youtube.com/vi/dj5s5PsAeMw/mqdefault.jpg"
            }
          ],
          stores: [
            {
              name: "Walmart",
              price: "$449.99",
              extracted_price: 449.99,
              link: "https://www.walmart.com",
              rating: 4.6,
              reviews: 1820,
              tag: "Best Price",
              details_and_offers: [
                "Free shipping on orders over $35",
                "Extended warranty available",
                "Easy 30-day returns"
              ],
              delivery_details: [
                { type: "Free shipping on $35+" },
                { type: "Ships in 2-3 business days" }
              ]
            },
            {
              name: "Amazon",
              price: "$459.99",
              extracted_price: 459.99,
              link: "https://www.amazon.com",
              rating: 4.5,
              reviews: 1205,
              tag: "Popular Choice",
              details_and_offers: [
                "Prime eligible - Free 2-day shipping",
                "Amazon Basics protection plan included",
                "30-day returns"
              ],
              delivery_details: [
                { type: "Free Prime shipping" },
                { type: "In stock - Ships today" }
              ]
            },
            {
              name: "Best Buy",
              price: "$469.99",
              extracted_price: 469.99,
              link: "https://www.bestbuy.com",
              rating: 4.7,
              reviews: 892,
              details_and_offers: [
                "Free in-store pickup available",
                "Geek Squad setup service available",
                "Best Buy Protection Plan included"
              ],
              delivery_details: [
                { type: "Free same-day delivery" },
                { type: "Ready for pickup today" }
              ]
            }
          ],
          about_the_product: {
            description: "Professional-grade 27-inch 4K monitor featuring USB-C connectivity, HDR support, and factory-calibrated color accuracy. Ideal for content creators, video editors, and gamers seeking pristine image quality.",
            features: [
              { title: "Screen Size", value: "27 inches" },
              { title: "Resolution", value: "3840 x 2160 (4K)" },
              { title: "Panel Type", value: "IPS" },
              { title: "Refresh Rate", value: "60Hz" },
              { title: "Response Time", value: "5ms" },
              { title: "Color Gamut", value: "99% Adobe RGB" },
              { title: "Brightness", value: "350 nits" },
              { title: "Inputs", value: "USB-C, HDMI x2, DisplayPort" }
            ]
          },
          ratings: [
            { stars: 5, amount: 950 },
            { stars: 4, amount: 650 },
            { stars: 3, amount: 150 },
            { stars: 2, amount: 40 },
            { stars: 1, amount: 10 }
          ]
        }
      }
    },
    aiVerdict: {
      verdict_score: 8.9,
      summary: "This is a professional-grade 4K monitor offering exceptional display quality and color accuracy, ideal for creative professionals. While it excels in performance and connectivity, potential buyers should be aware of its premium price and noted heat generation during extended use.",
      detailed_analysis: "This monitor represents excellent value in the professional 4K space. The USB-C connectivity with power delivery is increasingly important for modern workflows, eliminating cable clutter. The factory-calibrated color accuracy makes it suitable for professional color-critical work.",
      pros: [
        "Exceptional 4K color accuracy with 99% Adobe RGB coverage",
        "Convenient USB-C connectivity with power delivery",
        "Factory-calibrated for content creation",
        "Fully adjustable stand for ergonomic setup",
        "Low response time suitable for gaming and professional work",
        "Excellent build quality and materials"
      ],
      cons: [
        "Tends to run warm, requires good ventilation",
        "Premium price compared to 1440p alternatives",
        "Built-in speakers are mediocre",
        "Limited to 60Hz refresh rate (suitable for work but not gaming)"
      ],
      who_should_buy: [
        "Content creators and video editors",
        "Photographers and designers",
        "Professional gamers",
        "Developers and engineers",
        "Color graders and visual effects artists"
      ],
      who_should_avoid: [
        "Budget-conscious buyers",
        "Users sensitive to device heat",
        "Those who do not require professional-grade color accuracy and 4K resolution",
        "Casual gamers seeking high refresh rates"
      ],
      deal_breakers: [
        "Significant heat generation during extended use for setups without proper ventilation",
        "Lack of explicit warranty from major retailers (Walmart, Amazon)"
      ],
      best_for: "Professional creatives and gamers who demand exceptional color accuracy and image quality",
      comparison: "Outperforms Dell UltraSharp in color accuracy, comparable to ASUS ProArt in features"
    }
  },
  fp3: {
    // Product Basic Info
    id: "fp3",
    title: "Mechanical Gaming Keyboard",
    description: "RGB mechanical keyboard with custom switches and programmable keys.",
    price: 159.99,
    image_url: "https://aulaindia.com/wp-content/uploads/2022/09/F2066-II_1.jpg",
    product_url: "https://www.amazon.com/gp/product/B09XXXXXXXXX",
    source: "Amazon",
    source_id: null,
    imo_score: 8.7,
    site_rating: 4.5,
    reviews_count: 3200,
    like_count: 512,
    liked_by_user: false,
    created_at: new Date().toISOString(),
    pros: [
      "Responsive switches",
      "Beautiful RGB lighting",
      "Programmable keys",
      "Excellent build quality",
      "Great for gaming"
    ],
    cons: [
      "Quite loud",
      "Cable only (no wireless)",
      "Steep learning curve for macros"
    ],
    image_urls: [
      "https://aulaindia.com/wp-content/uploads/2022/09/F2066-II_1.jpg",
      "https://m.media-amazon.com/images/I/71L12GGZFCL._AC_SL1500_.jpg",
      "https://m.media-amazon.com/images/I/71Dq3U2FDZL._AC_SL1500_.jpg"
    ],
    brand: "GamerTech Pro",
    specifications: {
      "Switch Type": "Mechanical (Red Linear)",
      "Keycaps": "PBT Double-shot",
      "Layout": "Full Size (104 keys)",
      "Backlighting": "Per-key RGB",
      "Programmable Keys": "All keys",
      "Connection": "Wired USB 2.0",
      "Cable Length": "1.8 meters",
      "Weight": "1.2 kg",
      "Dimensions": "450mm x 145mm x 40mm",
      "Warranty": "2 years",
      "Software": "GamerTech Pro Control Center",
      "Switch Lifespan": "50 million keystrokes"
    },
    enrichedData: {
      description: "High-performance mechanical gaming keyboard featuring custom-tuned switches, vibrant RGB lighting system, and programmable macro keys. Designed for competitive gamers and professionals who demand responsive input and aesthetic appeal.",
      amazon_reviews: [
        {
          id: "R1",
          author: "Alex G.",
          rating: 5,
          title: "Perfect gaming keyboard!",
          content: "The switches are incredibly responsive and the build quality is outstanding. The RGB lighting is a nice touch. My only complaint is the noise level, but that's typical for mechanical keyboards.",
          is_verified: true,
          helpful_count: 312,
          timestamp: "2024-12-11"
        },
        {
          id: "R2",
          author: "Ryan M.",
          rating: 4,
          title: "Great keyboard, loud though",
          content: "Excellent responsiveness and durability. The programmable keys are a nice feature. Be warned - it's LOUD. If you share a room or workspace, your teammates might not appreciate the noise.",
          is_verified: true,
          helpful_count: 267,
          timestamp: "2024-11-30"
        }
      ],
      external_reviews: [
        {
          id: "E1",
          author: "Gaming Tech Reviews",
          rating: 4.5,
          title: "Best mechanical gaming keyboard for competitive play",
          content: "The responsiveness and build quality make this an excellent choice for serious gamers looking for a competitive edge.",
          source: "Gaming Tech Reviews"
        }
      ],
      immersive_data: {
        product_results: {
          title: "Mechanical Gaming Keyboard",
          user_reviews: [
            {
              text: "Love this keyboard! The switches feel amazing and the lighting is beautiful. Only downside is it's loud.",
              source: "amazon.com",
              rating: 5,
              date: "2024-12-16T00:00:00Z",
              user_name: "Pro Gamer"
            },
            {
              text: "Solid keyboard for the price. Great for gaming. Would be 5 stars if it had wireless option.",
              source: "newegg.com",
              rating: 4,
              date: "2024-12-07T00:00:00Z",
              user_name: "Tech Enthusiast"
            }
          ],
          videos: [
            {
              title: "Mechanical Gaming Keyboard - Pro Review",
              description: "Professional review of high-performance mechanical keyboard",
              link: "https://www.youtube.com/watch?v=iXROkS2rMV8",
              thumbnail: "https://img.youtube.com/vi/iXROkS2rMV8/mqdefault.jpg"
            },
            {
              title: "Best Mechanical Keyboard for Gaming",
              description: "Testing mechanical keyboard switches and response time for gaming",
              link: "https://www.youtube.com/watch?v=ktTEJjLl2o8",
              thumbnail: "https://img.youtube.com/vi/ktTEJjLl2o8/mqdefault.jpg"
            },
            {
              title: "Mechanical Keyboard - Unboxing & Setup",
              description: "Unboxing, setup, and first impressions of mechanical gaming keyboard",
              link: "https://www.youtube.com/watch?v=D_XtcI9yr9I",
              thumbnail: "https://img.youtube.com/vi/D_XtcI9yr9I/mqdefault.jpg"
            },
            {
              title: "RGB Mechanical Keyboard Features & Performance",
              description: "Detailed breakdown of RGB lighting, programmable macros, and performance",
              link: "https://www.youtube.com/watch?v=PNNAuT2b9c0",
              thumbnail: "https://img.youtube.com/vi/PNNAuT2b9c0/mqdefault.jpg"
            }
          ],
          stores: [
            {
              name: "Amazon",
              price: "$159.99",
              extracted_price: 159.99,
              link: "https://www.amazon.com",
              rating: 4.5,
              reviews: 3200,
              tag: "Popular Choice",
              details_and_offers: [
                "Prime eligible - Free 2-day shipping",
                "Amazon Basics warranty included",
                "30-day returns guarantee"
              ],
              delivery_details: [
                { type: "Free Prime 2-day shipping" },
                { type: "In stock - Ships today" }
              ]
            },
            {
              name: "Newegg",
              price: "$164.99",
              extracted_price: 164.99,
              link: "https://www.newegg.com",
              rating: 4.4,
              reviews: 1850,
              details_and_offers: [
                "Free standard shipping",
                "30-day return window",
                "Newegg warranty support"
              ],
              delivery_details: [
                { type: "Free standard shipping" },
                { type: "Ships in 3-5 business days" }
              ]
            },
            {
              name: "Best Buy",
              price: "$169.99",
              extracted_price: 169.99,
              link: "https://www.bestbuy.com",
              rating: 4.6,
              reviews: 945,
              tag: "Best Price",
              details_and_offers: [
                "Free in-store pickup available",
                "Gamers Club benefits - 10% off",
                "15% off for Best Buy members"
              ],
              delivery_details: [
                { type: "Free same-day delivery" },
                { type: "Pick up in 2 hours" }
              ]
            }
          ],
          about_the_product: {
            description: "High-performance mechanical gaming keyboard featuring custom-tuned switches, vibrant RGB lighting system, and programmable macro keys. Designed for competitive gamers and professionals who demand responsive input and aesthetic appeal.",
            features: [
              { title: "Switch Type", value: "Mechanical Red Linear" },
              { title: "Keycaps", value: "PBT Double-shot" },
              { title: "Layout", value: "Full Size (104 keys)" },
              { title: "Backlighting", value: "Per-key RGB" },
              { title: "Programmable Keys", value: "All keys" },
              { title: "Connection", value: "Wired USB 2.0" },
              { title: "Cable Length", value: "1.8 meters" },
              { title: "Switch Lifespan", value: "50 million keystrokes" }
            ]
          },
          ratings: [
            { stars: 5, amount: 1800 },
            { stars: 4, amount: 1200 },
            { stars: 3, amount: 150 },
            { stars: 2, amount: 40 },
            { stars: 1, amount: 10 }
          ]
        }
      }
    },
    aiVerdict: {
      verdict_score: 8.7,
      summary: "Excellent mechanical gaming keyboard with responsive switches and customizable RGB lighting. Perfect for competitive gamers and enthusiasts.",
      detailed_analysis: "This keyboard delivers the responsiveness that competitive gamers demand. The mechanical switches provide tactile feedback that significantly improves gaming performance. The build quality ensures this keyboard will last for years of heavy use.",
      pros: [
        "Highly responsive mechanical switches with 50M keystroke durability",
        "Eye-catching per-key RGB lighting system",
        "Fully programmable macro keys for competitive advantage",
        "Excellent build quality with PBT keycaps",
        "Great value for high-end gaming keyboard",
        "Intuitive software for customization"
      ],
      cons: [
        "Quite loud during use (typical for mechanical keyboards)",
        "Wired only (no wireless option)",
        "Steep learning curve for advanced macro programming",
        "Heavy for portability"
      ],
      who_should_buy: [
        "Competitive gamers",
        "Esports enthusiasts",
        "Mechanical keyboard enthusiasts",
        "Programmers and developers",
        "Anyone who values responsiveness over noise levels"
      ],
      who_should_avoid: [
        "Quiet environment requirements",
        "Users needing wireless connectivity",
        "Budget with strict constraints",
        "Those who share workspaces with noise-sensitive individuals"
      ],
      deal_breakers: [
        "Requires wired connection",
        "Significant noise output"
      ],
      best_for: "Serious gamers and enthusiasts who value responsive input and don't mind mechanical keyboard noise",
      comparison: "Rivals Corsair K95 Platinum in performance but at better price point"
    }
  }
};

export type DemoProductId = keyof typeof DEMO_PRODUCTS;
