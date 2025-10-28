import UIKit

class DashboardViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let welcomeLabel = UILabel()
    private let groupsButton = UIButton(type: .system)
    private let itemsButton = UIButton(type: .system)
    private let reportsButton = UIButton(type: .system)
    private let settingsButton = UIButton(type: .system)
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
        
        itemsButton.setTitle("Manage Items", for: .normal)
        itemsButton.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        itemsButton.backgroundColor = .systemGreen
        itemsButton.setTitleColor(.white, for: .normal)
        itemsButton.layer.cornerRadius = 12
        itemsButton.translatesAutoresizingMaskIntoConstraints = false
        itemsButton.addTarget(self, action: #selector(itemsTapped), for: .touchUpInside)

        reportsButton.setTitle("Reports", for: .normal)
        reportsButton.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        reportsButton.backgroundColor = .systemOrange
        reportsButton.setTitleColor(.white, for: .normal)
        reportsButton.layer.cornerRadius = 12
        reportsButton.translatesAutoresizingMaskIntoConstraints = false
        reportsButton.addTarget(self, action: #selector(reportsTapped), for: .touchUpInside)
        
        settingsButton.setTitle("Settings", for: .normal)
        settingsButton.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        settingsButton.backgroundColor = .systemGray
        settingsButton.setTitleColor(.white, for: .normal)
        settingsButton.layer.cornerRadius = 12
        settingsButton.translatesAutoresizingMaskIntoConstraints = false
        settingsButton.addTarget(self, action: #selector(settingsTapped), for: .touchUpInside)
        
        logoutButton.setTitle("Logout", for: .normal)
        logoutButton.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        logoutButton.setTitleColor(.systemRed, for: .normal)
        logoutButton.translatesAutoresizingMaskIntoConstraints = false
        logoutButton.addTarget(self, action: #selector(logoutTapped), for: .touchUpInside)
        
        contentView.addSubview(welcomeLabel)
        contentView.addSubview(groupsButton)
        contentView.addSubview(itemsButton)
        contentView.addSubview(reportsButton)
        contentView.addSubview(settingsButton)
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
            
            itemsButton.topAnchor.constraint(equalTo: groupsButton.bottomAnchor, constant: 20),
            itemsButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            itemsButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            itemsButton.heightAnchor.constraint(equalToConstant: 50),

            reportsButton.topAnchor.constraint(equalTo: itemsButton.bottomAnchor, constant: 20),
            reportsButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            reportsButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            reportsButton.heightAnchor.constraint(equalToConstant: 50),
            
            settingsButton.topAnchor.constraint(equalTo: reportsButton.bottomAnchor, constant: 20),
            settingsButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            settingsButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            settingsButton.heightAnchor.constraint(equalToConstant: 50),
            
            logoutButton.topAnchor.constraint(equalTo: settingsButton.bottomAnchor, constant: 40),
            logoutButton.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            logoutButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -40)
        ])
    }
    
    @objc private func groupsTapped() {
        let groupsVC = GroupsViewController()
        navigationController?.pushViewController(groupsVC, animated: true)
    }

    @objc private func reportsTapped() {
        let reportsVC = ReportsViewController()
        navigationController?.pushViewController(reportsVC, animated: true)
    }
    
    @objc private func itemsTapped() {
        let itemsVC = ItemsViewController()
        navigationController?.pushViewController(itemsVC, animated: true)
    }
    
    @objc private func settingsTapped() {
        let vc = SettingsViewController()
        navigationController?.pushViewController(vc, animated: true)
    }
    
    @objc private func logoutTapped() {
        let alert = UIAlertController(title: "Logout", message: "Are you sure you want to logout?", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Logout (Keep Password)", style: .default) { _ in
            // Clear session but keep saved credentials
            UserManager.shared.cookie = nil
            self.showLogin()
        })
        alert.addAction(UIAlertAction(title: "Logout (Clear All)", style: .destructive) { _ in
            // Clear everything including saved password
            UserManager.shared.clearAllData()
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