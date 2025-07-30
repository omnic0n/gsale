import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        print("🎭 SceneDelegate: Scene will connect")
        
        guard let windowScene = (scene as? UIWindowScene) else { return }
        
        // Create window if not already created by AppDelegate
        if window == nil {
            window = UIWindow(windowScene: windowScene)
        }
        
        // Set up the window if AppDelegate hasn't done it yet
        if window?.rootViewController == nil {
            let testVC = UIViewController()
            testVC.view.backgroundColor = .systemBlue
            testVC.title = "GSale Test"
            
            let testLabel = UILabel()
            testLabel.text = "GSale App is Working! 🎉"
            testLabel.textAlignment = .center
            testLabel.textColor = .white
            testLabel.font = UIFont.systemFont(ofSize: 24, weight: .bold)
            testLabel.translatesAutoresizingMaskIntoConstraints = false
            
            testVC.view.addSubview(testLabel)
            
            NSLayoutConstraint.activate([
                testLabel.centerXAnchor.constraint(equalTo: testVC.view.centerXAnchor),
                testLabel.centerYAnchor.constraint(equalTo: testVC.view.centerYAnchor)
            ])
            
            let navController = UINavigationController(rootViewController: testVC)
            window?.rootViewController = navController
        }
        
        window?.makeKeyAndVisible()
    }

    func sceneDidDisconnect(_ scene: UIScene) { }
    func sceneDidBecomeActive(_ scene: UIScene) { }
    func sceneWillResignActive(_ scene: UIScene) { }
    func sceneWillEnterForeground(_ scene: UIScene) { }
    func sceneDidEnterBackground(_ scene: UIScene) { }
} 