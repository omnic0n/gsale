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
            print("➡️ User not logged in, showing login screen")
            let loginVC = LoginViewController()
            window?.rootViewController = loginVC
        }
        
        window?.makeKeyAndVisible()
    }
} 