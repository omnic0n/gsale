import UIKit

class DashboardViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let welcomeLabel = UILabel()
    private let groupsButton = UIButton(type: .system)
    private let logoutButton = UIButton(type: .system)
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "GSale Dashboard"
        
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        let username = UserManager.shared.username ?? "User"
        welcomeLabel.text = "Welcome, \(username)!"
        welcomeLabel.font = UIFont.systemFont(ofSize: 24, weight: .bold)
        welcomeLabel.textAlignment = .center
        welcomeLabel.textColor = .label
        welcomeLabel.translatesAutoresizingMaskIntoConstraints = false
        
        groupsButton.setTitle("Manage Groups", for: .normal)
        groupsButton.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        groupsButton.backgroundColor = .systemBlue
        groupsButton.setTitleColor(.white, for: .normal)
        groupsButton.layer.cornerRadius = 12
        groupsButton.translatesAutoresizingMaskIntoConstraints = false
        groupsButton.addTarget(self, action: #selector(groupsTapped), for: .touchUpInside)
        
        logoutButton.setTitle("Logout", for: .normal)
        logoutButton.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        logoutButton.setTitleColor(.systemRed, for: .normal)
        logoutButton.translatesAutoresizingMaskIntoConstraints = false
        logoutButton.addTarget(self, action: #selector(logoutTapped), for: .touchUpInside)
        
        contentView.addSubview(welcomeLabel)
        contentView.addSubview(groupsButton)
        contentView.addSubview(logoutButton)
        
        setupConstraints()
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
            
            welcomeLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 60),
            welcomeLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            welcomeLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            groupsButton.topAnchor.constraint(equalTo: welcomeLabel.bottomAnchor, constant: 60),
            groupsButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            groupsButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            groupsButton.heightAnchor.constraint(equalToConstant: 50),
            
            logoutButton.topAnchor.constraint(equalTo: groupsButton.bottomAnchor, constant: 40),
            logoutButton.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            logoutButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -40)
        ])
    }
    
    @objc private func groupsTapped() {
        let groupsVC = GroupsViewController()
        navigationController?.pushViewController(groupsVC, animated: true)
    }
    
    @objc private func logoutTapped() {
        let alert = UIAlertController(title: "Logout", message: "Are you sure you want to logout?", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Logout", style: .destructive) { _ in
            UserManager.shared.logout()
            self.showLogin()
        })
        present(alert, animated: true)
    }
    
    private func showLogin() {
        let loginVC = LoginViewController()
        let navController = UINavigationController(rootViewController: loginVC)
        navController.modalPresentationStyle = .fullScreen
        present(navController, animated: true)
    }
} 