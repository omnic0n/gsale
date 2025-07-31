import UIKit

class LoginViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let logoImageView = UIImageView()
    private let titleLabel = UILabel()
    private let subtitleLabel = UILabel()
    
    private let usernameTextField = UITextField()
    private let passwordTextField = UITextField()
    private let savePasswordSwitch = UISwitch()
    private let savePasswordLabel = UILabel()
    private let loginButton = UIButton(type: .system)
    private let activityIndicator = UIActivityIndicatorView(style: .large)
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadSavedCredentials()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        attemptAutoLogin()
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
        
        subtitleLabel.text = "Inventory Management"
        subtitleLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        subtitleLabel.textAlignment = .center
        subtitleLabel.textColor = .secondaryLabel
        
        setupTextField(usernameTextField, placeholder: "Username", icon: "person.fill")
        setupTextField(passwordTextField, placeholder: "Password", icon: "lock.fill")
        passwordTextField.isSecureTextEntry = true
        
        savePasswordLabel.text = "Save Password"
        savePasswordLabel.font = UIFont.systemFont(ofSize: 16)
        savePasswordLabel.textColor = .label
        savePasswordLabel.translatesAutoresizingMaskIntoConstraints = false
        
        savePasswordSwitch.translatesAutoresizingMaskIntoConstraints = false
        savePasswordSwitch.onTintColor = .systemBlue
        
        loginButton.setTitle("Login", for: .normal)
        loginButton.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        loginButton.backgroundColor = .systemBlue
        loginButton.setTitleColor(.white, for: .normal)
        loginButton.layer.cornerRadius = 12
        loginButton.translatesAutoresizingMaskIntoConstraints = false
        loginButton.addTarget(self, action: #selector(loginTapped), for: .touchUpInside)
        
        activityIndicator.hidesWhenStopped = true
        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        
        contentView.addSubview(logoImageView)
        contentView.addSubview(titleLabel)
        contentView.addSubview(subtitleLabel)
        contentView.addSubview(usernameTextField)
        contentView.addSubview(passwordTextField)
        contentView.addSubview(savePasswordLabel)
        contentView.addSubview(savePasswordSwitch)
        contentView.addSubview(loginButton)
        contentView.addSubview(activityIndicator)
        
        setupConstraints()
    }
    
    private func setupTextField(_ textField: UITextField, placeholder: String, icon: String) {
        textField.placeholder = placeholder
        textField.font = UIFont.systemFont(ofSize: 16)
        textField.borderStyle = .roundedRect
        textField.backgroundColor = .secondarySystemBackground
        textField.translatesAutoresizingMaskIntoConstraints = false
        
        let imageView = UIImageView(image: UIImage(systemName: icon))
        imageView.tintColor = .secondaryLabel
        imageView.contentMode = .scaleAspectFit
        imageView.frame = CGRect(x: 0, y: 0, width: 20, height: 20)
        
        let containerView = UIView()
        containerView.frame = CGRect(x: 0, y: 0, width: 30, height: 20)
        containerView.addSubview(imageView)
        imageView.center = containerView.center
        
        textField.leftView = containerView
        textField.leftViewMode = .always
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
            
            logoImageView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 60),
            logoImageView.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            logoImageView.widthAnchor.constraint(equalToConstant: 80),
            logoImageView.heightAnchor.constraint(equalToConstant: 80),
            
            titleLabel.topAnchor.constraint(equalTo: logoImageView.bottomAnchor, constant: 20),
            titleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            subtitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            subtitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            usernameTextField.topAnchor.constraint(equalTo: subtitleLabel.bottomAnchor, constant: 40),
            usernameTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            usernameTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            usernameTextField.heightAnchor.constraint(equalToConstant: 50),
            
            passwordTextField.topAnchor.constraint(equalTo: usernameTextField.bottomAnchor, constant: 16),
            passwordTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            passwordTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            passwordTextField.heightAnchor.constraint(equalToConstant: 50),
            
            savePasswordLabel.topAnchor.constraint(equalTo: passwordTextField.bottomAnchor, constant: 20),
            savePasswordLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            
            savePasswordSwitch.centerYAnchor.constraint(equalTo: savePasswordLabel.centerYAnchor),
            savePasswordSwitch.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            loginButton.topAnchor.constraint(equalTo: savePasswordLabel.bottomAnchor, constant: 24),
            loginButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            loginButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            loginButton.heightAnchor.constraint(equalToConstant: 50),
            loginButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -40),
            
            activityIndicator.centerXAnchor.constraint(equalTo: loginButton.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: loginButton.centerYAnchor)
        ])
    }
    
    @objc private func loginTapped() {
        guard let username = usernameTextField.text, !username.isEmpty,
              let password = passwordTextField.text, !password.isEmpty else {
            showAlert(title: "Error", message: "Please enter both username and password")
            return
        }
        
        loginButton.isEnabled = false
        activityIndicator.startAnimating()
        
        Task {
            do {
                let response = try await NetworkManager.shared.login(username: username, password: password)
                
                await MainActor.run {
                    self.activityIndicator.stopAnimating()
                    self.loginButton.isEnabled = true
                    
                    if response.success {
                        let passwordToSave = self.savePasswordSwitch.isOn ? password : nil
                        UserManager.shared.saveLoginData(
                            cookie: response.cookie ?? "",
                            username: response.username ?? username,
                            userId: response.user_id,
                            isAdmin: response.is_admin ?? false,
                            password: passwordToSave
                        )
                        self.showDashboard()
                    } else {
                        self.showAlert(title: "Login Failed", message: response.message)
                    }
                }
            } catch {
                await MainActor.run {
                    self.activityIndicator.stopAnimating()
                    self.loginButton.isEnabled = true
                    
                    let errorMessage: String
                    switch error {
                    case NetworkError.unauthorized:
                        errorMessage = "Invalid username or password. Please check your credentials."
                    case NetworkError.serverError(let message):
                        errorMessage = "Server error: \(message)"
                    default:
                        errorMessage = "Login failed. Please check your internet connection and try again."
                    }
                    
                    self.showAlert(title: "Login Failed", message: errorMessage)
                }
            }
        }
    }
    
    private func showDashboard() {
        let dashboardVC = DashboardViewController()
        let navController = UINavigationController(rootViewController: dashboardVC)
        navController.modalPresentationStyle = .fullScreen
        present(navController, animated: true)
    }
    
    private func loadSavedCredentials() {
        if let credentials = UserManager.shared.getStoredCredentials() {
            usernameTextField.text = credentials.username
            passwordTextField.text = credentials.password
            savePasswordSwitch.isOn = true
            print("📱 Loaded saved credentials for user: \(credentials.username)")
        }
    }
    
    private func attemptAutoLogin() {
        // Only auto-login if user is already logged in (has valid session)
        if UserManager.shared.isLoggedIn() {
            print("🔄 User already logged in, showing dashboard")
            showDashboard()
        } else if UserManager.shared.hasStoredCredentials() {
            print("🔄 Found saved credentials, but not logged in - user can manually login")
        }
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
} 