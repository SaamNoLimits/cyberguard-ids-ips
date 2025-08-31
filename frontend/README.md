# Cybersecurity Dashboard Frontend

A modern, real-time cybersecurity monitoring dashboard built with Next.js 14, TypeScript, and Tailwind CSS.

## 🚀 Features

- **Real-time Threat Monitoring**: Live WebSocket updates for threat detection
- **Interactive Dashboard**: Modern UI with threat statistics and visualizations
- **Threat Management**: Manual block/unblock capabilities for detected threats
- **Detailed Analysis**: Click-through threat details with forensic information
- **Responsive Design**: Mobile-friendly interface with dark/light mode support
- **Advanced Filtering**: Search, filter, and paginate through threats

## 🛠️ Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI primitives
- **State Management**: React hooks and context
- **Real-time**: WebSocket integration
- **Icons**: Lucide React icons

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🔧 Configuration

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── dashboard-home/     # Main dashboard page
│   ├── threat-monitoring/  # Threat monitoring page
│   └── rule-management/    # IDS rules management
├── components/             # Reusable UI components
│   ├── ui/                # Base UI components (Radix)
│   ├── threat-details-modal.tsx
│   └── dashboard-layout.tsx
├── hooks/                  # Custom React hooks
├── lib/                   # Utility functions and API client
└── styles/                # Global styles and Tailwind config
```

## 🎨 Key Components

### ThreatMonitoring (`/threat-monitoring`)
- Real-time threat feed with WebSocket integration
- Interactive threat table with sorting and filtering
- Click-to-view detailed threat analysis
- Manual threat blocking/unblocking controls

### ThreatDetailsModal
- Comprehensive threat information display
- Tabbed interface (Overview, Analysis, Recommendations, Mitigation)
- Security recommendations based on attack type
- Real-time status updates

### DashboardHome (`/dashboard-home`)
- Overview statistics and charts
- Recent threats summary
- System health indicators
- Quick action buttons

## 🔌 API Integration

The frontend communicates with the FastAPI backend through:

### REST API (`/lib/api.ts`)
```typescript
// Threat management
await blockThreat(threatId)
await unblockThreat(threatId)
await getThreatDetails(threatId)

// Statistics
await getStats()
await getRecentThreats(limit)
```

### WebSocket Connection
```typescript
// Real-time threat updates
const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL)
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === 'new_threat') {
    // Handle new threat alert
  }
}
```

## 🎯 Usage

### Development
1. Start the backend API server first
2. Run `npm run dev` to start the frontend
3. Navigate to `http://localhost:3000`

### Production
1. Build the application: `npm run build`
2. Start the production server: `npm start`
3. Configure reverse proxy (nginx) if needed

## 🔐 Security Features

### Threat Visualization
- **Real-time Alerts**: Instant threat notifications
- **Risk Assessment**: Color-coded threat levels (LOW/MEDIUM/HIGH/CRITICAL)
- **Attack Classification**: Visual indicators for attack types
- **Geolocation**: IP-based attack source mapping

### Interactive Controls
- **Manual Blocking**: One-click threat blocking
- **Bulk Actions**: Multi-select threat management
- **Filter Presets**: Quick filter for specific attack types
- **Export Functionality**: Download threat reports

## 📊 Dashboard Sections

### 1. Overview Dashboard
- Total threats detected
- Active/blocked threats ratio
- Attack type distribution
- Recent activity timeline

### 2. Threat Monitoring
- Live threat feed
- Advanced filtering options
- Detailed threat inspection
- Manual response controls

### 3. Rule Management
- IDS rule configuration
- Custom detection rules
- Rule performance metrics
- Import/export capabilities

## 🚨 Real-time Features

### WebSocket Events
- `new_threat`: New threat detected
- `threat_blocked`: Threat blocked/unblocked
- `system_status`: System health updates
- `stats_update`: Statistics refresh

### Auto-refresh
- Threat list auto-updates every 10 seconds
- Statistics refresh every 30 seconds
- Connection status monitoring
- Graceful reconnection handling

## 🎨 UI/UX Features

### Modern Design
- Clean, professional interface
- Consistent color scheme
- Intuitive navigation
- Responsive layout

### Accessibility
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode

## 🔧 Customization

### Theming
Modify `tailwind.config.js` for custom themes:
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {...},
        secondary: {...}
      }
    }
  }
}
```

### Components
All UI components are modular and customizable through props and CSS classes.

## 📱 Mobile Support

- Responsive design for all screen sizes
- Touch-friendly interface
- Mobile-optimized navigation
- Progressive Web App (PWA) ready

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check backend server is running
   - Verify WebSocket URL in `.env.local`
   - Check firewall settings

2. **API Requests Failing**
   - Verify backend API URL
   - Check CORS configuration
   - Ensure backend is accessible

3. **Build Errors**
   - Clear `.next` directory
   - Delete `node_modules` and reinstall
   - Check TypeScript errors

## 📈 Performance

### Optimization Features
- Next.js automatic code splitting
- Image optimization
- Static generation where possible
- Efficient re-rendering with React hooks

### Monitoring
- Real-time performance metrics
- Error boundary implementation
- Loading states for better UX
- Optimistic updates for actions

## 🔄 Updates

To update the dashboard:
1. Pull latest changes
2. Run `npm install` for new dependencies
3. Restart development server
4. Clear browser cache if needed
