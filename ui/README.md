# Kwanzaa Semantic Search Explorer UI

A comprehensive React-based user interface for searching the Kwanzaa corpus with full provenance tracking, citation management, and analytics.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

## Features

- **Natural Language Search**: Query the Kwanzaa corpus using natural language
- **Advanced Filtering**: Filter by namespace, year range, content type, source, and tags
- **Citation Export**: Export results in BibTeX, APA, MLA, JSON, and CSV formats
- **Search History**: Save and manage search history with favorites
- **Analytics Dashboard**: Track search metrics and usage patterns
- **Full Provenance**: Every result includes complete metadata and citations

## Technology Stack

- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Zustand (state management)
- Vitest (testing)
- AIKit (ready for integration)

## Project Structure

```
ui/
├── src/
│   ├── components/       # React components
│   ├── hooks/           # Custom hooks
│   ├── services/        # API services
│   ├── stores/          # State management
│   ├── types/           # TypeScript types
│   ├── utils/           # Utility functions
│   └── App.tsx          # Main app
├── public/
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

The UI expects the Kwanzaa backend to be running on `localhost:8000`:

```bash
# In backend directory
cd ../backend
uvicorn app.main:app --reload
```

## Documentation

See [docs/ui/SEARCH_EXPLORER.md](../docs/ui/SEARCH_EXPLORER.md) for comprehensive documentation.

## License

Apache 2.0
