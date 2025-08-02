import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        print("🎭 SceneDelegate: Scene will connect")
        
        guard let windowScene = (scene as? UIWindowScene) else { return }
        
        window = UIWindow(windowScene: windowScene)
        
        // Check if user is already logged in
        if UserManager.shared.isLoggedIn() {
            print("🔄 User already logged in, showing dashboard")
            let dashboardVC = DashboardViewController()
            let navController = UINavigationController(rootViewController: dashboardVC)
            window?.rootViewController = navController
        } else {
            print("🔐 User not logged in, showing login screen")
            let loginVC = LoginViewController()
            window?.rootViewController = loginVC
        }
        
        window?.makeKeyAndVisible()
        
        // Handle URL if app was launched with one
        if let urlContext = connectionOptions.urlContexts.first {
            handleIncomingURL(urlContext.url)
        }
    }
    
    func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {
        // Handle OAuth callback URLs
        guard let url = URLContexts.first?.url else { return }
        handleIncomingURL(url)
    }
    
    private func handleIncomingURL(_ url: URL) {
        print("🔗 Handling incoming URL: \(url)")
        
        // Check if this is an OAuth callback
        if url.scheme == "gsaleapp" && url.host == "oauth-callback" {
            handleOAuthCallback(url: url)
        }
    }
    
    private func handleOAuthCallback(url: URL) {
        print("🔄 Processing OAuth callback: \(url)")
        
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let queryItems = components.queryItems else {
            showOAuthError("Invalid callback URL")
            return
        }
        
        // Check for error
        if let error = queryItems.first(where: { $0.name == "error" })?.value {
            showOAuthError("OAuth error: \(error)")
            return
        }
        
        // This callback will be handled by ASWebAuthenticationSession
        // The NetworkManager will process the response
        print("✅ OAuth callback received successfully")
    }
    
    private func showOAuthError(_ message: String) {
        print("❌ OAuth Error: \(message)")
        
        DispatchQueue.main.async {
            if let topViewController = self.window?.rootViewController {
                let alert = UIAlertController(title: "Authentication Error", message: message, preferredStyle: .alert)
                alert.addAction(UIAlertAction(title: "OK", style: .default))
                topViewController.present(alert, animated: true)
            }
        }
    }
    
    private func showDashboard() {
        DispatchQueue.main.async {
            let dashboardVC = DashboardViewController()
            let navController = UINavigationController(rootViewController: dashboardVC)
            self.window?.rootViewController = navController
            self.window?.makeKeyAndVisible()
        }
    }

    func sceneDidDisconnect(_ scene: UIScene) { }
    func sceneDidBecomeActive(_ scene: UIScene) { }
    func sceneWillResignActive(_ scene: UIScene) { }
    func sceneWillEnterForeground(_ scene: UIScene) { }
    func sceneDidEnterBackground(_ scene: UIScene) { }
} 