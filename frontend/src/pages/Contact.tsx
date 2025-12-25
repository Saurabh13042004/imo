import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { 
  Mail, 
  MessageSquare, 
  Zap, 
  Bug, 
  Clock,
  CheckCircle2,
  ArrowRight,
  Send,
  AlertCircle,
  Phone,
  MapPin
} from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";

const API_URL = import.meta.env.VITE_API_URL;

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Validate form data
      if (!formData.name.trim() || !formData.email.trim() || !formData.subject.trim() || !formData.message.trim()) {
        toast.error("Please fill in all fields");
        setLoading(false);
        return;
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        toast.error("Please enter a valid email address");
        setLoading(false);
        return;
      }

      // Submit to API
      const response = await fetch(`${API_URL}/api/v1/contact/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to submit form");
      }

      toast.success("✨ Message sent successfully!\nWe'll get back to you within 24 hours.", {
        duration: 4000,
        icon: "🎉"
      });

      // Reset form
      setFormData({ name: "", email: "", subject: "", message: "" });
    } catch (error) {
      console.error("Contact form error:", error);
      toast.error(error instanceof Error ? error.message : "Failed to submit form. Please try again.", {
        duration: 4000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/20">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"></div>
      </div>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 pt-32">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge variant="secondary" className="mb-6 px-4 py-1.5 text-sm font-semibold">
              <MessageSquare className="w-3.5 h-3.5 mr-2 inline" />
              Get in Touch
            </Badge>
            
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
              Let's Talk
              <span className="block bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-transparent bg-clip-text">
                About Your Needs
              </span>
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed mb-8">
              Whether you have questions, feedback, or need support, our team is here to help. 
              We're passionate about making your experience exceptional.
            </p>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="flex items-center justify-center gap-4 flex-wrap"
            >
              <Badge variant="outline" className="px-3 py-1.5">
                <Clock className="w-3.5 h-3.5 mr-2 inline" />
                24-hour response time
              </Badge>
              <Badge variant="outline" className="px-3 py-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 mr-2 inline" />
                Expert support team
              </Badge>
            </motion.div>
          </motion.div>
        </div>
      </section>



      {/* Main Contact Form Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Send Us a Message
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Fill out the form below and we'll get back to you as soon as possible. 
              All fields are required.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            viewport={{ once: true }}
          >
            <Card className="border-0 shadow-2xl overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
              
              <CardContent className="p-8 md:p-10">
                <form onSubmit={handleSubmit} className="space-y-7">
                  {/* Name and Email Row */}
                  <div className="grid md:grid-cols-2 gap-6">
                    <motion.div 
                      className="space-y-3"
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                    >
                      <Label htmlFor="name" className="text-sm font-semibold text-foreground flex items-center gap-2">
                        <span>Full Name</span>
                        <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="John Doe"
                        className="h-11 bg-muted/50 border-0 focus:bg-background transition-colors"
                        required
                      />
                    </motion.div>

                    <motion.div 
                      className="space-y-3"
                      initial={{ opacity: 0, x: 10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                    >
                      <Label htmlFor="email" className="text-sm font-semibold text-foreground flex items-center gap-2">
                        <span>Email Address</span>
                        <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="john@example.com"
                        className="h-11 bg-muted/50 border-0 focus:bg-background transition-colors"
                        required
                      />
                    </motion.div>
                  </div>
                  
                  {/* Subject */}
                  <motion.div 
                    className="space-y-3"
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                  >
                    <Label htmlFor="subject" className="text-sm font-semibold text-foreground flex items-center gap-2">
                      <span>Subject</span>
                      <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      placeholder="How can we assist you?"
                      className="h-11 bg-muted/50 border-0 focus:bg-background transition-colors"
                      required
                    />
                  </motion.div>
                  
                  {/* Message */}
                  <motion.div 
                    className="space-y-3"
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                  >
                    <Label htmlFor="message" className="text-sm font-semibold text-foreground flex items-center gap-2">
                      <span>Message</span>
                      <span className="text-red-500">*</span>
                    </Label>
                    <Textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      placeholder="Tell us more about your inquiry..."
                      rows={7}
                      className="bg-muted/50 border-0 focus:bg-background transition-colors resize-none"
                      required
                    />
                    <p className="text-xs text-muted-foreground">
                      {formData.message.length}/1000
                    </p>
                  </motion.div>
                  
                  {/* Submit Button */}
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                  >
                    <Button 
                      type="submit" 
                      className="w-full h-12 text-base font-semibold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:shadow-xl transition-all duration-300" 
                      disabled={loading}
                    >
                      {loading ? (
                        <span className="flex items-center gap-2">
                          <div className="animate-spin">⚙️</div>
                          Sending...
                        </span>
                      ) : (
                        <span className="flex items-center gap-2">
                          <Send className="w-4 h-4" />
                          Send Message
                        </span>
                      )}
                    </Button>
                  </motion.div>
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Form Tips */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            className="mt-12 grid md:grid-cols-3 gap-6"
          >
            <Card className="border bg-muted/30 shadow-sm">
              <CardContent className="p-6 space-y-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-950/50 flex items-center justify-center">
                  <AlertCircle className="w-5 h-5 text-blue-600" />
                </div>
                <h4 className="font-semibold">Be Specific</h4>
                <p className="text-sm text-muted-foreground">
                  The more details you provide, the better we can assist you.
                </p>
              </CardContent>
            </Card>

            <Card className="border bg-muted/30 shadow-sm">
              <CardContent className="p-6 space-y-3">
                <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-950/50 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-purple-600" />
                </div>
                <h4 className="font-semibold">Quick Response</h4>
                <p className="text-sm text-muted-foreground">
                  We aim to respond to all inquiries within 24 hours.
                </p>
              </CardContent>
            </Card>

            <Card className="border bg-muted/30 shadow-sm">
              <CardContent className="p-6 space-y-3">
                <div className="w-10 h-10 rounded-lg bg-pink-100 dark:bg-pink-950/50 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-pink-600" />
                </div>
                <h4 className="font-semibold">Confirmation Email</h4>
                <p className="text-sm text-muted-foreground">
                  You'll receive a confirmation email after submission.
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              Common Questions
            </h2>
            <p className="text-lg text-muted-foreground">
              Find quick answers to frequently asked questions
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                q: "What's your typical response time?",
                a: "We typically respond to all inquiries within 24 hours. Urgent matters may be addressed sooner."
              },
              {
                q: "Can I report a security issue?",
                a: "Yes, please email imhollc27@gmail.com with details. Security reports are treated with highest priority."
              },
              {
                q: "How can I suggest a feature?",
                a: "We'd love to hear your ideas! Use the Product Feedback option to share feature suggestions."
              },
              {
                q: "Is there a phone support option?",
                a: "Currently, we support communication via email. For urgent matters, include 'URGENT' in the subject line."
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="border bg-background shadow-sm hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <h4 className="font-semibold mb-3 flex items-start gap-2">
                      <span className="text-primary mt-1">Q.</span>
                      {item.q}
                    </h4>
                    <p className="text-sm text-muted-foreground leading-relaxed flex gap-2">
                      <span className="text-muted-foreground/60 mt-0.5">A.</span>
                      {item.a}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center"
        >
          <Card className="border-0 shadow-2xl bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
            
            <CardContent className="p-10 md:p-16">
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
                Ready to Get Started?
              </h2>
              <p className="text-lg text-muted-foreground mb-8 leading-relaxed">
                Have questions before diving in? Our support team is here to help you get the most out of IMO.
              </p>
              <Button 
                size="lg"
                className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:shadow-xl transition-all duration-300 text-base font-semibold"
                onClick={() => document.querySelector('#name')?.scrollIntoView({ behavior: 'smooth' })}
              >
                <MessageSquare className="w-5 h-5 mr-2" />
                Send a Message
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </section>
    </div>
  );
};

export default Contact;