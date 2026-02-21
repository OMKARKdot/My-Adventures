#!/bin/bash

# My Adventures - Vercel Deployment Script
# This script helps deploy your website to Vercel

set -e

echo "🚀 My Adventures - Vercel Deployment Script"
echo "=========================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "   npm install -g vercel"
    exit 1
fi

# Check if logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please log in to Vercel first:"
    echo "   vercel login"
    exit 1
fi

echo "✅ Vercel CLI is installed and you're logged in"
echo ""

# Check if this is a git repository
if [ ! -d ".git" ]; then
    echo "⚠️  Warning: This doesn't appear to be a git repository."
    echo "   Consider initializing git for better deployment tracking:"
    echo "   git init && git add . && git commit -m 'Initial commit'"
    echo ""
fi

# Check for required files
echo "📋 Checking required files..."
required_files=("index.html" "vercel.json" "package.json")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo ""
    echo "❌ Missing required files: ${missing_files[*]}"
    echo "   Please ensure all required files are present before deploying."
    exit 1
fi

echo ""
echo "🔍 Validating configuration..."

# Validate vercel.json
if command -v jq &> /dev/null; then
    if jq . vercel.json > /dev/null 2>&1; then
        echo "   ✅ vercel.json is valid JSON"
    else
        echo "   ❌ vercel.json contains invalid JSON"
        exit 1
    fi
else
    echo "   ⚠️  jq not installed, skipping JSON validation"
fi

# Check for HTML files
html_files=$(find . -name "*.html" -type f | wc -l)
echo "   📄 Found $html_files HTML files"

# Check for image files
image_files=$(find . -name "*.webp" -o -name "*.jpeg" -o -name "*.jpg" -o -name "*.png" -type f | wc -l)
echo "   🖼️  Found $image_files image files"

echo ""
echo "🚀 Starting deployment..."

# Deploy to Vercel
echo "   Deploying to Vercel..."
vercel_output=$(vercel --yes 2>&1)
deployment_url=$(echo "$vercel_output" | grep -E "https://.*\.vercel\.app" | head -1)

if [ $? -eq 0 ]; then
    echo "   ✅ Deployment successful!"
    echo "   🌐 Preview URL: $deployment_url"
else
    echo "   ❌ Deployment failed!"
    echo "$vercel_output"
    exit 1
fi

echo ""
echo "🎯 Production deployment?"

read -p "   Do you want to deploy to production? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Deploying to production..."
    vercel_output=$(vercel --prod --yes 2>&1)
    prod_url=$(echo "$vercel_output" | grep -E "https://.*\.vercel\.app" | head -1)
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Production deployment successful!"
        echo "   🌐 Production URL: $prod_url"
    else
        echo "   ❌ Production deployment failed!"
        echo "$vercel_output"
        exit 1
    fi
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Visit your deployed site: $deployment_url"
echo "   2. Test all pages and functionality"
echo "   3. Consider setting up a custom domain"
echo "   4. Add analytics if needed"
echo "   5. Monitor performance in Vercel Dashboard"
echo ""
echo "📚 For more information, see README-VERCEL.md"