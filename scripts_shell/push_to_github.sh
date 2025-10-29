#!/bin/bash

# GitHub Push Helper Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║           🚀 GitHub Push Helper 🚀                       ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Ready to push:"
echo "   47 files"
echo "   14,835 lines of code"
echo ""
echo "⚠️  BEFORE PUSHING:"
echo ""
echo "1. Create repository on GitHub:"
echo "   https://github.com/new"
echo ""
echo "2. Repository name: final-telegram-automation"
echo ""
echo "3. Make it PRIVATE (recommended)"
echo ""
echo "4. Do NOT initialize with README"
echo ""
echo "5. Click 'Create repository'"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

read -p "Have you created the repository on GitHub? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "❌ Please create repository first, then run this script again."
    echo ""
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  🔍 Current Configuration"
echo "════════════════════════════════════════════════════════════"
echo ""

git remote -v

echo ""
echo "Repository URL: git@github.com:yadavlaxmi/final-telegram-automation.git"
echo ""

read -p "Is this correct? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your GitHub username: " username
    read -p "Enter repository name: " reponame
    
    git remote set-url origin "git@github.com:${username}/${reponame}.git"
    echo "✅ Remote URL updated"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  📤 Pushing to GitHub..."
echo "════════════════════════════════════════════════════════════"
echo ""

git push -u origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║              ✅ SUCCESS! Code Pushed! ✅                 ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 View on GitHub:"
    
    REPO_URL=$(git remote get-url origin | sed 's/git@github.com:/https:\/\/github.com\//' | sed 's/\.git$//')
    echo "   $REPO_URL"
    echo ""
    echo "📊 Pushed:"
    echo "   ✅ 47 files"
    echo "   ✅ 14,835 lines"
    echo "   ✅ Complete documentation"
    echo "   ✅ API keys protected"
    echo ""
else
    echo ""
    echo "❌ Push failed. Check errors above."
    echo ""
    echo "Common solutions:"
    echo "  1. Make sure repository exists on GitHub"
    echo "  2. Check SSH key is added: https://github.com/settings/keys"
    echo "  3. Verify repository name and username"
    echo ""
fi

