# GSale iOS App

This is the iOS frontend for the GSale application, a sales and inventory management system.

## Project Structure

```
gsale/
├── AppDelegate.swift              # App entry point and lifecycle management
├── SceneDelegate.swift            # Scene lifecycle management
├── Info.plist                    # App configuration
├── Main.storyboard              # Main storyboard with login and dashboard
├── LaunchScreen.storyboard       # Launch screen
├── Assets.xcassets/             # App icons and images
├── Managers/
│   ├── NetworkManager.swift      # API communication with Flask backend
│   └── UserManager.swift        # User session management
└── ViewControllers/
    ├── LoginViewController.swift     # Login screen
    ├── DashboardViewController.swift # Main dashboard
    ├── ItemsViewController.swift     # Items list
    ├── GroupsViewController.swift    # Groups list
    ├── ExpensesViewController.swift  # Expenses list
    ├── ReportsViewController.swift   # Reports dashboard
    └── AdminViewController.swift     # Admin panel
```

## Features

### Core Functionality
- **Login System**: Secure authentication with the Flask backend
- **Dashboard**: Overview of key metrics (profit, sales, purchases, expenses)
- **Items Management**: View and manage inventory items
- **Groups Management**: Organize items into groups
- **Expenses Tracking**: Monitor business expenses
- **Reports**: View financial reports and analytics
- **Admin Panel**: User management for administrators

### Technical Features
- **Session Management**: Persistent login sessions using UserDefaults
- **Network Layer**: Robust API communication with error handling
- **Modern UI**: Native iOS design with Auto Layout
- **Pull-to-Refresh**: Data refresh functionality
- **Error Handling**: User-friendly error messages

## Setup Instructions

### Prerequisites
- Xcode 12.0 or later
- iOS 14.0 or later
- Active internet connection for API calls

### Installation
1. Open the project in Xcode
2. Select your development team in the project settings
3. Build and run the project on a simulator or device

### Configuration
The app is configured to connect to the Flask backend at:
- **Production**: `https://gsale.levimylesllc.com`
- **Development**: Update the `baseURL` in `NetworkManager.swift` if needed

## API Endpoints

The app communicates with the following Flask endpoints:

- `POST /login` - User authentication
- `GET /dashboard` - Dashboard data
- `GET /items` - Items list
- `GET /groups` - Groups list
- `GET /expenses` - Expenses list
- `GET /reports` - Reports data
- `GET /admin/users` - Users list (admin only)

## Architecture

### Network Layer
- `NetworkManager`: Singleton class handling all API requests
- Uses `URLSession` for network communication
- Implements proper error handling and response parsing
- Supports session cookies for authentication

### Data Models
- `LoginResponse`: Authentication response
- `DashboardData`: Dashboard metrics
- `Item`: Item information
- `Group`: Group information
- `Expense`: Expense details
- `ReportsData`: Financial reports
- `User`: User information

### User Management
- `UserManager`: Handles user session persistence
- Stores session cookies, user ID, username, and admin status
- Provides login/logout functionality
- Manages session state across app launches

## Development Notes

### Current Status
This is a **placeholder implementation** with basic UI and navigation. The following features need to be implemented:

- **Add/Edit Functionality**: Create forms for adding/editing items, groups, expenses
- **Admin Actions**: Implement user management features (add, delete, toggle admin)
- **Data Persistence**: Local caching for offline functionality
- **Push Notifications**: Real-time updates
- **Advanced UI**: Charts, graphs, and enhanced visualizations

### Next Steps
1. Implement CRUD operations for all entities
2. Add form validation and error handling
3. Implement offline data caching
4. Add search and filtering capabilities
5. Enhance UI with charts and graphs
6. Add push notifications for real-time updates

## Backend Integration

The iOS app is designed to work with the existing Flask backend. Ensure the backend is running and accessible before testing the iOS app.

### Authentication Flow
1. User enters credentials
2. App sends POST request to `/login`
3. Backend validates credentials and returns session cookie
4. App stores session cookie for subsequent requests
5. All API requests include the session cookie

### Error Handling
- Network errors are displayed to the user
- Authentication failures redirect to login
- Invalid responses show appropriate error messages

## Contributing

When adding new features:
1. Follow the existing code structure
2. Use proper error handling
3. Implement loading states
4. Add appropriate user feedback
5. Test on both simulator and device

## License

This project is part of the GSale application suite. 