# Semantic Search Explorer UI

## Overview

The Kwanzaa Semantic Search Explorer is a comprehensive React-based UI for searching the Kwanzaa corpus with full provenance tracking, citation management, and analytics. Built with AIKit components and designed to work seamlessly with the ZeroDB backend.

## Features

### 1. Search Interface
- Natural language query input with debouncing
- Real-time search execution
- Loading states and error handling
- Clear and re-submit functionality

### 2. Advanced Filtering
- **Namespace Selector**: Choose from 6 predefined namespaces
  - Primary Sources
  - Black Press
  - Speeches & Letters
  - Black STEM
  - Teaching Kits
  - Development Patterns

- **Year Range Filter**: Dual slider with numeric inputs (1600-2026)
- **Content Type Filter**: Multi-select checkboxes for:
  - Speech
  - Letter
  - Proclamation
  - Article
  - Book
  - Report
  - Testimony
  - Interview

- **Active Filter Chips**: Visual display of applied filters with quick removal

### 3. Search Results
- Ranked result cards with relevance scores
- Visual score indicators (gradient bars)
- Expandable content previews
- Query term highlighting
- Comprehensive provenance metadata:
  - Citation label (prominent)
  - Canonical URL (clickable)
  - Source organization
  - Year
  - Content type
  - License
  - Tags

### 4. Citation Export
- **Multiple Formats**:
  - BibTeX
  - APA
  - MLA
  - JSON
  - CSV

- **Per-Result Actions**:
  - One-click copy to clipboard
  - Visual feedback on copy
  - Expandable citation formats

- **Bulk Export**:
  - Export all results in chosen format
  - Automatic file download

### 5. Search History
- Persistent storage of recent searches
- Favorite searches with star icon
- Quick re-run of saved searches
- Filter by favorites
- Clear all history
- Shows timestamp and applied filters

### 6. Analytics Dashboard
- **Key Metrics**:
  - Total searches
  - Average search time
  - Filters used count

- **Visualizations**:
  - Most queried namespaces (bar chart)
  - Filter usage patterns (bar chart)
  - Relevance score distribution (histogram)

- **Real-time Updates**: Analytics update after each search

## Architecture

### Technology Stack
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand with persistence
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Testing**: Vitest + Testing Library
- **AIKit Integration**: Ready for AIKit packages

### Project Structure
```
ui/
├── src/
│   ├── components/          # React components
│   │   ├── SearchBar.tsx
│   │   ├── FilterPanel.tsx
│   │   ├── SearchResults.tsx
│   │   ├── SearchResultCard.tsx
│   │   ├── SearchHistory.tsx
│   │   ├── AnalyticsDashboard.tsx
│   │   └── __tests__/       # Component tests
│   ├── hooks/               # Custom React hooks
│   │   ├── useSearch.ts
│   │   └── useDebounce.ts
│   ├── services/            # API and utility services
│   │   ├── searchApi.ts
│   │   ├── exportService.ts
│   │   └── __tests__/
│   ├── stores/              # Zustand stores
│   │   └── searchStore.ts
│   ├── types/               # TypeScript definitions
│   │   ├── search.ts
│   │   └── aikit.ts
│   ├── utils/               # Utility functions
│   │   ├── format.ts
│   │   ├── namespaces.ts
│   │   └── __tests__/
│   ├── App.tsx              # Main application
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Installation

```bash
cd ui

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Type check
npm run type-check

# Lint
npm run lint
```

## Configuration

### Environment Variables
Create a `.env` file in the `ui/` directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend Integration
The UI expects the backend to be running on `localhost:8000`. The Vite dev server is configured to proxy API requests:

```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## Usage

### Basic Search
1. Enter your query in the search bar
2. Click "Search" or press Enter
3. Results appear with relevance scores and full metadata

### Applying Filters
1. Select a namespace from the filter panel
2. Adjust year range using sliders or inputs
3. Check content types to include
4. Active filters appear as removable chips

### Exporting Citations
**Per Result**:
1. Click "Show citation formats" on any result card
2. Click BibTeX, APA, or MLA to copy to clipboard
3. Citation is automatically copied

**Bulk Export**:
1. Click "Export" in results header
2. Choose format (BibTeX, APA, MLA, JSON, CSV)
3. File downloads automatically

### Managing Search History
1. Click "History" tab in header
2. View all previous searches
3. Click star icon to favorite
4. Click search to re-run
5. Filter by favorites only
6. Remove individual searches or clear all

### Viewing Analytics
1. Click "Analytics" tab in header
2. View aggregate metrics
3. Analyze namespace usage patterns
4. Review filter usage statistics
5. See relevance score distribution

## AIKit Integration

The UI is designed to integrate with AIKit components. Placeholder types are defined in `src/types/aikit.ts`:

### Planned AIKit Components
- `useAIStream`: For streaming search requests
- `AgentResponse`: For rendering search results
- `ToolResult`: For displaying retrieval information
- `StreamingToolResult`: For streaming search updates
- `MarkdownRenderer`: For rendering chunk text
- `CodeBlock`: For citation displays
- `UsageDashboard`: For comprehensive analytics

### Integration Pattern
```typescript
// Example AIKit integration
import { useAIStream, AgentResponse } from '@ainative/ai-kit-react';

function SearchResults() {
  const { data, isStreaming } = useAIStream({
    endpoint: '/api/v1/search/semantic',
    method: 'POST',
    body: searchRequest,
  });

  return (
    <AgentResponse
      data={data}
      showMetadata={true}
    />
  );
}
```

## Testing

### Running Tests
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test SearchBar.test.tsx

# Run in watch mode
npm test -- --watch

# Open test UI
npm run test:ui
```

### Test Coverage
Current test coverage includes:
- Component rendering and interaction
- Service functions (export, API calls)
- Utility functions (formatting, namespaces)
- Store mutations and persistence

### Writing Tests
```typescript
// Component test example
import { render, screen } from '@testing-library/react';
import { SearchBar } from '../SearchBar';

it('renders search input', () => {
  render(<SearchBar value="" onChange={vi.fn()} onSearch={vi.fn()} />);
  expect(screen.getByRole('textbox')).toBeInTheDocument();
});
```

## Accessibility

### WCAG 2.1 AA Compliance
- All interactive elements keyboard accessible
- ARIA labels on icon-only buttons
- Focus indicators on all focusable elements
- Color contrast ratios meet AA standards
- Screen reader friendly structure

### Keyboard Navigation
- `Tab`: Navigate between elements
- `Enter`: Submit search, activate buttons
- `Escape`: Close modals/dropdowns
- `Arrow keys`: Navigate sliders

## Performance

### Optimizations
- Debounced search input (300ms)
- Lazy loading for large result sets
- Memoized expensive calculations
- Efficient re-renders with Zustand
- Code splitting via Vite

### Bundle Size
- Main bundle: ~200KB (gzipped)
- Lazy chunks: ~50KB each
- Total initial load: <500KB

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Backend Connection Issues
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend
# Ensure frontend origin is allowed
```

### Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Test Failures
```bash
# Update snapshots
npm test -- -u

# Run tests in verbose mode
npm test -- --reporter=verbose
```

## Future Enhancements

### Planned Features
1. **Voice Search**: Web Speech API integration
2. **Advanced Query Operators**: Boolean, proximity, wildcards
3. **Result Annotations**: User notes and highlights
4. **Collaborative Collections**: Share search results
5. **API Key Management**: For authenticated requests
6. **Offline Mode**: Service worker for offline search history

### AIKit Enhancements
1. Full AIKit component integration
2. Streaming search results
3. Real-time observability dashboard
4. RLHF feedback collection
5. Advanced tool result rendering

## Contributing

### Development Workflow
1. Create feature branch from `main`
2. Implement feature with tests
3. Ensure all tests pass
4. Run type check and linter
5. Submit pull request

### Code Style
- Follow TypeScript best practices
- Use functional components with hooks
- Prefer composition over inheritance
- Write self-documenting code
- Add JSDoc comments for complex logic

### Commit Guidelines
- Use conventional commits format
- Reference issue numbers
- Keep commits atomic and focused

## License

Apache 2.0 - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [kwanzaa/issues](https://github.com/AINative-Studio/kwanzaa/issues)
- Documentation: [/docs](https://github.com/AINative-Studio/kwanzaa/tree/main/docs)
