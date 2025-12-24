import { MetaTags } from '@/components/seo';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  Mail,
  FileText,
  Heart,
  Lock,
  Ban,
  Flag
} from 'lucide-react';

const ReviewGuidelines = () => {
  const handleReport = () => {
    const subject = encodeURIComponent('Report Review Violation - IMO');
    const body = encodeURIComponent(
      'Please describe the violation:\n\n' +
      'Review URL: \n' +
      'Violation Type: \n' +
      'Details: \n\n' +
      'Thank you for helping keep IMO safe and helpful!'
    );
    window.location.href = `mailto:imhollc27@gmail.com?subject=${subject}&body=${body}`;
  };

  return (
    <>
      <MetaTags
        title="Review Submission Guidelines | IMO"
        description="IMO Review Submission Guidelines - Learn how to submit honest, helpful, and respectful product reviews that benefit the entire community."
        keywords="review guidelines, submission rules, community guidelines, video upload rules, IMO reviews"
        canonicalUrl="https://informedmarketopinions.com/review-guidelines"
      />
      
      <div className="min-h-screen bg-background">
        {/* Header */}
        <div className="bg-gradient-to-br from-primary/10 via-background to-secondary/10 border-b">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center space-y-4">
              <Badge variant="outline" className="mb-4">
                <Shield className="mr-2 h-4 w-4" />
                Community Guidelines
              </Badge>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
                IMO Video Upload Guidelines
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                These guidelines help keep our community helpful, respectful, and focused on genuine product experiences.
              </p>
              <p className="text-sm text-muted-foreground">
                Last updated: December 2025
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Agreement Notice */}
          <Card className="mb-8 border-primary/20 bg-primary/5">
            <CardContent className="pt-6">
              <p className="text-center text-sm">
                <strong>By submitting a review, you agree to follow these rules.</strong> IMO reserves the right to remove any content that violates them and may suspend accounts for repeated or severe violations.
              </p>
            </CardContent>
          </Card>

          {/* Report Button */}
          <div className="mb-8 flex justify-center">
            <Button 
              onClick={handleReport}
              size="lg"
              variant="destructive"
              className="gap-2"
            >
              <Flag className="h-5 w-5" />
              Report a Violation
            </Button>
          </div>

          {/* Guidelines Sections */}
          <div className="space-y-6">
            {/* 1. Be Honest and Relevant */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <CheckCircle className="h-6 w-6 text-blue-600" />
                  </div>
                  <span>1. Be Honest and Relevant</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>Share your own personal experience with the product.</li>
                  <li>Focus on the product itself: performance, quality, features, value, etc.</li>
                  <li>Avoid unrelated topics, rants, personal attacks, or off-topic content.</li>
                </ul>
              </CardContent>
            </Card>

            {/* 2. Keep It Respectful and Civil */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Heart className="h-6 w-6 text-green-600" />
                  </div>
                  <span>2. Keep It Respectful and Civil</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>Use polite, professional language — no profanity, hate speech, harassment, or derogatory remarks.</li>
                  <li>No name-calling, insults, or threats toward brands, companies, other users, or individuals.</li>
                </ul>
              </CardContent>
            </Card>

            {/* 3. No Inappropriate or Explicit Content */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <Ban className="h-6 w-6 text-red-600" />
                  </div>
                  <span>3. No Inappropriate or Explicit Content</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>No nudity, sexually explicit material, violence, gore, or graphic content.</li>
                  <li>No links or references to adult websites, illegal activities, or harmful content.</li>
                </ul>
              </CardContent>
            </Card>

            {/* 4. Keep Reviews Clear and Concise */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <FileText className="h-6 w-6 text-purple-600" />
                  </div>
                  <span>4. Keep Reviews Clear and Concise</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>Aim for short, focused reviews (ideally 50–300 words).</li>
                  <li>Avoid excessive repetition, all-caps yelling, or excessive punctuation.</li>
                </ul>
              </CardContent>
            </Card>

            {/* 5. No Spam, Advertising, or Misinformation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <AlertTriangle className="h-6 w-6 text-yellow-600" />
                  </div>
                  <span>5. No Spam, Advertising, or Misinformation</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>No promotional content, affiliate links, or self-advertising.</li>
                  <li>No fake reviews, bots, or paid endorsements.</li>
                  <li>No false claims, unverified medical/health advice, or misleading statements.</li>
                </ul>
              </CardContent>
            </Card>

            {/* 6. Respect Copyright and Intellectual Property */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <Lock className="h-6 w-6 text-indigo-600" />
                  </div>
                  <span>6. Respect Copyright and Intellectual Property</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>Only upload content you own or have permission to share (e.g., photos/videos of the product you purchased).</li>
                  <li>Do not post copyrighted material without authorization.</li>
                </ul>
              </CardContent>
            </Card>

            {/* 7. No Illegal or Harmful Content */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <Shield className="h-6 w-6 text-red-600" />
                  </div>
                  <span>7. No Illegal or Harmful Content</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>No content that promotes illegal activities, discrimination, or harm to others.</li>
                  <li>No personal information about yourself or others.</li>
                </ul>
              </CardContent>
            </Card>

            {/* 8. Moderation and Consequences */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <AlertTriangle className="h-6 w-6 text-orange-600" />
                  </div>
                  <span>8. Moderation and Consequences</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>All reviews are subject to moderation.</li>
                  <li>Violations may result in removal of the review and/or suspension of your account.</li>
                  <li>Repeated violations will lead to permanent account termination.</li>
                </ul>
              </CardContent>
            </Card>

            {/* 9. Reporting Violations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-pink-100 rounded-lg">
                    <Flag className="h-6 w-6 text-pink-600" />
                  </div>
                  <span>9. Reporting Violations</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  If you see a review that violates these guidelines, please use the "Report" button or contact us directly.
                </p>
                <Button 
                  onClick={handleReport}
                  variant="outline"
                  className="gap-2"
                >
                  <Mail className="h-4 w-4" />
                  Email: imhollc27@gmail.com
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Footer Message */}
          <Card className="mt-12 bg-gradient-to-r from-primary/10 to-secondary/10 border-primary/20">
            <CardContent className="pt-6">
              <p className="text-center font-medium">
                Thank you for helping keep IMO a trusted and helpful community!
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
};

export default ReviewGuidelines;
