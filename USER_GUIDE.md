# 📖 User Guide - Semantic Book Recommender

Welcome! This guide will help you make the most of the Semantic Book Recommender.


## 🎯 What Can This Do?

The Semantic Book Recommender helps you discover books by understanding what you're looking for - not just keywords, but the actual meaning behind your description.

### Key Features

- **Semantic Search** - Describe what you want in natural language
- **Smart Filtering** - Filter by category and emotional tone
- **Personal Library** - Save favorites and track search history
- **Fast & Efficient** - Intelligent caching for instant results

## 🚀 Getting Started

### First Time Setup

1. **Open the application** in your browser (usually `http://localhost:7860`)
2. **You're ready!** No login required - the app creates a default user automatically

---

## 🔍 Searching for Books

### Basic Search

1. **Navigate to the Search tab** (🔍 icon)
2. **Type your description** in the search box

**Example searches:**
```
"A mystery thriller with unexpected twists"
"A heartwarming story about friendship and loss"
"Science fiction exploring artificial intelligence"
"Historical fiction set during World War II"
"A self-help book about productivity"
```

3. **Click "🔍 Search Books"**
4. **Browse the results** in the gallery below

### Tips for Better Searches

✅ **DO:**
- Be specific and descriptive
- Mention themes, settings, or emotions
- Use natural language
- Try different phrasings

❌ **DON'T:**
- Use just one or two keywords
- Expect exact title matches
- Search for specific authors (use filters instead)

### Examples

| What You Want | Good Search | Why It Works |
|---------------|-------------|--------------|
| Action novel | "Fast-paced adventure with lots of action" | Describes the feeling |
| Romance | "A romantic story with emotional depth" | Captures the essence |
| Learn coding | "Beginner-friendly book about programming" | States the goal |
| Mystery | "A detective story with clever plot twists" | Describes the experience |


## 🎛️ Using Filters

### Category Filter

**Purpose:** Narrow results to specific book types

**Options:**
- **All** - No filtering (default)
- **Fiction** - Novels, stories
- **Non-fiction** - Educational, informational
- **Biography** - Life stories
- **History** - Historical accounts
- **Science** - Scientific topics
- **And more...**

**How to use:**
1. Enter your search query
2. Select a category from the dropdown
3. Click search

### Emotional Tone Filter

**Purpose:** Sort books by their emotional content

**Options:**
- **All** - No preference (default)
- **Happy** - Uplifting, joyful content
- **Sad** - Emotional, melancholic
- **Suspenseful** - Thrilling, tense
- **Surprising** - Unexpected, twist-filled
- **Angry** - Intense, confrontational

**How to use:**
1. Enter your search query
2. Select a tone from the dropdown
3. Click search

**The results will be sorted** with books matching your chosen tone appearing first.


## 📚 Viewing Book Details

### See Full Information

1. **Click any book** in the search results
2. **The details panel** appears on the right

**Details Include:**
- **Title** - Full book title
- **Authors** - All authors (nicely formatted)
- **Category** - Book classification
- **ISBN-13** - Unique identifier
- **Emotion Scores** - Joy, Surprise, Anger, Fear, Sadness ratings
- **Favorite Status** - Whether you've favorited it
- **Description** - Complete book description

### Understanding Emotion Scores

Scores range from **0.00 to 1.00**:
- **0.00-0.20** - Very low
- **0.21-0.40** - Low
- **0.41-0.60** - Moderate
- **0.61-0.80** - High
- **0.81-1.00** - Very high

**Example:**
```
Joy: 0.78       (High - uplifting content)
Surprise: 0.45  (Moderate - some twists)
Anger: 0.12     (Very low - calm tone)
Fear: 0.65      (High - suspenseful)
Sadness: 0.23   (Low - not melancholic)
```


## ⭐ Managing Favorites

### Adding to Favorites

**From Search Tab:**
1. **Search for books** you're interested in
2. **Click a book** to see its details
3. **Click "⭐ Add to Favorites"** button
4. **Star appears** on the book cover (⭐)
5. **Button disables** (can't add same book twice)

**Visual Indicators:**
- ⭐ (Filled star) = Favorited
- ☆ (Empty star) = Not favorited

### Viewing Favorites

1. **Go to the Favorites tab** (⭐ icon)
2. **See all your saved books** in one place
3. **Click any book** to see full details

### Removing from Favorites

**From Favorites Tab:**
1. **Go to Favorites tab**
2. **Click the book** you want to remove
3. **Click "💔 Remove from Favorites"** button
4. **Book disappears** from favorites gallery


## 📜 Viewing Search History

### Access History

1. **Go to the History tab** (📜 icon)
2. **See a table** of all your searches

### History Information

Each entry shows:
- **Query** - What you searched for
- **Filters** - Category and/or tone you used
- **Results** - How many books were found
- **Time** - When you searched

### Using History

**Benefits:**
- Track what you've searched for
- Re-run successful searches
- See your reading interests over time

**Refresh:**
- Click "🔄 Refresh History" to update the view


## ⚙️ Settings & Statistics

### User Statistics

**In the Settings tab**, you can see:
- **Username** - Your user identifier
- **Total Searches** - How many searches you've made
- **Favorites** - Number of books favorited
- **Member Since** - When you first used the app

### Cache Statistics

**Performance metrics:**
- **Entries** - Cached items
- **Hits** - Times cache was used
- **Misses** - Times cache wasn't used
- **Hit Rate** - Percentage of cached results
- **TTL** - How long cache entries last

**Good hit rate:** 60-70% means searches are fast!

### Clearing Cache

**When to do it:**
- Testing different searches
- App feels slow
- Want fresh results

**How:**
1. Go to Settings tab
2. Click "🗑️ Clear Cache"
3. Confirmation appears

**Note:** This doesn't delete your favorites or history!

---

## 💡 Tips & Tricks

### Search Optimization

1. **Start broad, then filter**
   ```
   Search: "detective story"
   Filter: Category = Fiction, Tone = Suspenseful
   ```

2. **Use descriptive phrases**
   ```
   Instead of: "space"
   Try: "space exploration and colonization"
   ```

3. **Mention specific elements**
   ```
   "A romance set in Victorian England with strong female lead"
   ```

### Discovering New Books

1. **Try unexpected combinations**
   ```
   Search: "philosophy"
   Tone: Happy
   Result: Uplifting philosophical works
   ```

2. **Explore different categories**
   ```
   Your usual: Fiction
   Try: Biography or History
   ```

3. **Use emotion filters creatively**
   ```
   Category: Non-fiction
   Tone: Surprising
   Result: Eye-opening educational books
   ```

### Managing Your Library

1. **Favorite liberally** - You can always remove later
2. **Check history** - Find searches that worked well
3. **Use favorites as wishlist** - Books you want to read

---

## ⚡ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Focus search box | `Ctrl + /` or `Cmd + /` |
| Submit search | `Enter` in search box |
| Switch tabs | `Tab` (when focused on tabs) |


## 🔍 Understanding Results

### Why These Books?

Results are ranked by **semantic similarity**:
1. Your search is converted to a **meaning vector**
2. Books are scored by **how similar** their descriptions are
3. Filters further **refine and sort** the results

### Star Icons Meaning

| Icon | Meaning |
|------|---------|
| ⭐ | You've favorited this book |
| ☆ | Not in your favorites |

### Result Count

- **Default:** Up to 16 books shown
- **Sorted by:** Relevance (and tone if selected)
- **Filtered by:** Category (if selected)


## ❓ Common Questions

### "No books found"

**Possible reasons:**
1. Search too specific
2. No books match filters
3. Typos in search

**Try:**
- Broader search terms
- Remove filters
- Different phrasing

### "Slow search"

**Normal on first search:** ~2-3 seconds
**Should be instant:** on repeat searches (caching)

**If consistently slow:**
1. Check your internet connection
2. Check cache hit rate in Settings
3. Clear cache and try again

### "Can't favorite a book"

**Reasons:**
1. Already favorited (button disabled)
2. Book not selected (click book first)

**Solution:**
- Click book to see details
- Button will enable if not already favorited

### "Lost my favorites"

**Favorites are persistent!** They're stored in a database.

**Check:**
1. Go to Favorites tab
2. Click "🔄 Refresh Favorites"
3. If using Docker, check volume mounts

---

## 🎨 Interface Guide

### Tab Navigation

```
┌─────────────────────────────────────┐
│  🔍 Search | 📜 History | ⭐ Favorites | ⚙️ Settings
└─────────────────────────────────────┘
```

- **Search** - Main search interface
- **History** - Past searches
- **Favorites** - Saved books
- **Settings** - Stats and cache management

### Search Tab Layout

```
┌──────────────────────────────────────┐
│  Search Box + Filters                │
│  [Search Books Button]               │
├──────────────────────────────────────┤
│  Results Gallery (4 columns)         │
├──────────────────────────────────────┤
│  Book Details  │  Actions            │
│                │  [Add to Favorites] │
└──────────────────────────────────────┘
```

### Favorites Tab Layout

```
┌──────────────────────────────────────┐
│  Favorites Gallery (4 columns)       │
├──────────────────────────────────────┤
│  Book Details  │  Actions            │
│                │  [Remove]           │
├──────────────────────────────────────┤
│  [Refresh Favorites]                 │
└──────────────────────────────────────┘
```

---

## 🛡️ Privacy & Data

### What's Stored

**Locally:**
- Your search history
- Your favorites
- User statistics
- Cache data (temporary)

**Not Stored:**
- No personal information
- No login credentials
- No browsing history outside the app

### Data Location

**If running locally:**
- Database: `./data/app.db`
- Cache: In memory (temporary)

**If using Docker:**
- Data persists in mounted volumes
- Can be backed up separately



## 🆘 Troubleshooting

### Application Issues

| Problem | Solution |
|---------|----------|
| Can't access app | Check if running on port 7860 |
| Search not working | Check internet connection |
| No results | Try broader search terms |
| Slow performance | Clear cache in Settings |


## 🎯 Best Practices

### For Best Results

1. **Search Tips:**
   - Be descriptive but concise
   - Include mood and themes
   - Use filters strategically

2. **Favorites Management:**
   - Add books as you find them
   - Review favorites periodically
   - Remove books you've read

3. **Regular Maintenance:**
   - Check history weekly
   - Clean up old favorites monthly
   - Monitor search patterns


## 📈 Improving Your Experience

### Learn from History

1. **Check successful searches**
   - What queries found good books?
   - Which filters worked best?
   - What patterns emerge?

2. **Refine your approach**
   - Adapt successful query styles
   - Experiment with new combinations
   - Build your search vocabulary

### Optimize Performance

1. **Leverage caching**
   - Repeat good searches
   - Check cache hit rate
   - Clear only when needed

2. **Use filters wisely**
   - Start without filters
   - Add filters to refine
   - Remove if too restrictive


**Happy book hunting!** 📚✨

For technical support, see the [README](README.md) or [Docker Guide](DOCKER_GUIDE.md).