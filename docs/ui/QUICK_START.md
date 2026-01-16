# Semantic Search Explorer - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Node.js 18+ and npm 9+
- Kwanzaa backend running on `localhost:8000`

### Installation

```bash
# 1. Navigate to UI directory
cd /Users/aideveloper/kwanzaa/ui

# 2. Install dependencies (if not already installed)
npm install

# 3. Copy environment template
cp .env.example .env

# 4. Start development server
npm run dev
```

The application will be available at: **http://localhost:3000**

### First Search

1. Open http://localhost:3000 in your browser
2. Enter a query: "Civil Rights Act 1964"
3. Click "Search" or press Enter
4. Browse results with full provenance metadata

### Key Features to Try

#### 1. Apply Filters
- Select a namespace from the left panel
- Adjust year range with sliders
- Check content types to filter

#### 2. Export Citations
- Click "Show citation formats" on any result
- Click BibTeX, APA, or MLA to copy
- Use "Export" button for bulk downloads

#### 3. View Search History
- Click "History" tab in header
- Star favorite searches
- Click any search to re-run it

#### 4. Check Analytics
- Click "Analytics" tab in header
- View search metrics and patterns
- See relevance score distribution

## Project Structure

```
ui/
├── src/
│   ├── components/          # UI components
│   │   ├── SearchBar.tsx
│   │   ├── FilterPanel.tsx
│   │   ├── SearchResults.tsx
│   │   └── ...
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   ├── stores/             # State management
│   ├── types/              # TypeScript types
│   └── utils/              # Utilities
├── package.json
└── vite.config.ts
```

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm test             # Run tests
npm run test:ui      # Open test UI
npm run lint         # Lint code
npm run type-check   # TypeScript type checking
```

## Backend Integration

The UI connects to the Kwanzaa backend API:

**Endpoints Used**:
- `POST /api/v1/search/semantic` - Semantic search
- `GET /api/v1/search/namespaces` - List namespaces

**Proxy Configuration** (in `vite.config.ts`):
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## Environment Variables

Create `.env` file:
```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_DEBUG=false
```

## Troubleshooting

### Backend Not Running
```bash
# Start backend in separate terminal
cd ../backend
uvicorn app.main:app --reload
```

### Port Already in Use
```bash
# Change port in vite.config.ts
server: {
  port: 3001,  # Change to any available port
}
```

### Dependencies Issue
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Testing

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test SearchBar.test.tsx

# Open interactive test UI
npm run test:ui
```

## Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview

# Output directory: dist/
```

## Next Steps

1. **Explore the UI**: Try different searches and filters
2. **Read Documentation**: See [SEARCH_EXPLORER.md](./SEARCH_EXPLORER.md)
3. **Check Implementation**: Review [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
4. **Install AIKit**: Add AIKit packages when available
5. **Customize**: Modify components to fit your needs

## Key Components

### SearchBar
Natural language search input with debouncing

### FilterPanel
Advanced filtering with namespace, year, content type

### SearchResults
Paginated results with full provenance metadata

### SearchResultCard
Individual result with citation export

### SearchHistory
Saved searches with favorites and re-run

### AnalyticsDashboard
Search metrics and usage patterns

## Support

- **Documentation**: `/docs/ui/`
- **Issues**: GitHub Issues
- **Code**: `/ui/src/`

## License

Apache 2.0
