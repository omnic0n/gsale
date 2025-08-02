import UIKit
import AuthenticationServices

class LoginViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let logoImageView = UIImageView()
    private let titleLabel = UILabel()
    private let subtitleLabel = UILabel()
    
    // Google Sign-In button only
    private let googleSignInButton = UIButton(type: .system)
    
    private let activityIndicator = UIActivityIndicatorView(style: .medium)
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        logoImageView.image = UIImage(systemName: "cart.fill")
        logoImageView.tintColor = .systemBlue
        logoImageView.contentMode = .scaleAspectFit
        logoImageView.translatesAutoresizingMaskIntoConstraints = false
        
        titleLabel.text = "GSale"
        titleLabel.font = UIFont.systemFont(ofSize: 32, weight: .bold)
        titleLabel.textAlignment = .center
        titleLabel.textColor = .label
        
        subtitleLabel.text = "Manage your sales with ease"
        subtitleLabel.font = UIFont.systemFont(ofSize: 16, weight: .regular)
        subtitleLabel.textAlignment = .center
        subtitleLabel.textColor = .secondaryLabel
        subtitleLabel.numberOfLines = 0
        
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        subtitleLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Setup Google Sign-In Button
        setupGoogleSignInButton()
        
        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        activityIndicator.hidesWhenStopped = true
        
        contentView.addSubview(logoImageView)
        contentView.addSubview(titleLabel)
        contentView.addSubview(subtitleLabel)
        contentView.addSubview(googleSignInButton)
        contentView.addSubview(activityIndicator)
    }
    
    private func setupGoogleSignInButton() {
        var config = UIButton.Configuration.filled()
        config.title = "Sign in with Google"
        config.baseBackgroundColor = UIColor(red: 66/255, green: 133/255, blue: 244/255, alpha: 1.0) // Google Blue
        config.baseForegroundColor = .white
        config.cornerStyle = .fixed
        config.background.cornerRadius = 12
        
        // Add Google icon
        if let googleIcon = UIImage(systemName: "globe") {
            config.image = googleIcon
            config.imagePadding = 10
            config.imagePlacement = .leading
        }
        
        googleSignInButton.configuration = config
        googleSignInButton.translatesAutoresizingMaskIntoConstraints = false
        googleSignInButton.addTarget(self, action: #selector(googleSignInTapped), for: .touchUpInside)
    }
    
    @objc private func googleSignInTapped() {
        Task {
            do {
                let result = try await NetworkManager.shared.initiateGoogleSignIn()
                
                DispatchQueue.main.async {
                    if result.success {
                        UserManager.shared.saveLoginData(
                            cookie: result.cookie ?? "",
                            username: result.username ?? "",
                            userId: result.user_id ?? 0,
                            isAdmin: result.is_admin ?? false
                        )
                        
                        let dashboardVC = DashboardViewController()
                        let navController = UINavigationController(rootViewController: dashboardVC)
                        
                        if let window = self.view.window {
                            window.rootViewController = navController
                            UIView.transition(with: window, duration: 0.3, options: .transitionCrossDissolve, animations: nil)
                        }
                    } else {
                        let alert = UIAlertController(
                            title: "Login Failed",
                            message: result.message,
                            preferredStyle: .alert
                        )
                        alert.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alert, animated: true)
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    let alert = UIAlertController(
                        title: "Login Failed",
                        message: error.localizedDescription,
                        preferredStyle: .alert
                    )
                    alert.addAction(UIAlertAction(title: "OK", style: .default))
                    self.present(alert, animated: true)
                }
            }
        }
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            
            logoImageView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 100),
            logoImageView.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            logoImageView.widthAnchor.constraint(equalToConstant: 80),
            logoImageView.heightAnchor.constraint(equalToConstant: 80),
            
            titleLabel.topAnchor.constraint(equalTo: logoImageView.bottomAnchor, constant: 20),
            titleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            subtitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            subtitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            googleSignInButton.topAnchor.constraint(equalTo: subtitleLabel.bottomAnchor, constant: 60),
            googleSignInButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 40),
            googleSignInButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -40),
            googleSignInButton.heightAnchor.constraint(equalToConstant: 50),
            googleSignInButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -100),
            
            activityIndicator.centerXAnchor.constraint(equalTo: googleSignInButton.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: googleSignInButton.centerYAnchor)
        ])
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    private func presentDashboard() {
        let dashboardVC = DashboardViewController()
        let navController = UINavigationController(rootViewController: dashboardVC)
        
        // Replace the root view controller
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let window = windowScene.windows.first {
            window.rootViewController = navController
            window.makeKeyAndVisible()
        }
    }
} 