import UIKit

class AdminViewController: UIViewController {
    
    private let tableView = UITableView()
    private let refreshControl = UIRefreshControl()
    private let addButton = UIButton(type: .system)
    
    private var users: [User] = []
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
        setupTableView()
        setupActions()
        setupNavigationBar()
        loadUsers()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Admin Panel"
        
        // Add button
        addButton.setTitle("Add User", for: .normal)
        addButton.backgroundColor = .systemBlue
        addButton.setTitleColor(.white, for: .normal)
        addButton.layer.cornerRadius = 8
        addButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(addButton)
        
        // Table view
        tableView.translatesAutoresizingMaskIntoConstraints = false
        tableView.backgroundColor = .systemBackground
        view.addSubview(tableView)
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            addButton.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            addButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            addButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            addButton.heightAnchor.constraint(equalToConstant: 44),
            
            tableView.topAnchor.constraint(equalTo: addButton.bottomAnchor, constant: 16),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }
    
    private func setupTableView() {
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(AdminUserTableViewCell.self, forCellReuseIdentifier: "AdminUserCell")
        tableView.refreshControl = refreshControl
    }
    
    private func setupActions() {
        addButton.addTarget(self, action: #selector(addUserButtonTapped), for: .touchUpInside)
        refreshControl.addTarget(self, action: #selector(refreshData), for: .valueChanged)
    }
    
    private func setupNavigationBar() {
        navigationItem.leftBarButtonItem = UIBarButtonItem(title: "Back", style: .plain, target: self, action: #selector(backButtonTapped))
    }
    
    private func loadUsers() {
        NetworkManager.shared.getUsers { [weak self] result in
            DispatchQueue.main.async {
                self?.refreshControl.endRefreshing()
                
                switch result {
                case .success(let users):
                    self?.users = users
                    self?.tableView.reloadData()
                case .failure(let error):
                    self?.showAlert(title: "Error", message: error.localizedDescription)
                }
            }
        }
    }
    
    @objc private func refreshData() {
        loadUsers()
    }
    
    @objc private func addUserButtonTapped() {
        showAlert(title: "Add User", message: "This feature will be implemented soon.")
    }
    
    @objc private func backButtonTapped() {
        navigationController?.popViewController(animated: true)
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

extension AdminViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return users.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "AdminUserCell", for: indexPath) as! AdminUserTableViewCell
        let user = users[indexPath.row]
        cell.configure(with: user)
        return cell
    }
}

extension AdminViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        return 80
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let user = users[indexPath.row]
        showAlert(title: user.username, message: "User management options will be shown here.")
    }
}

class AdminUserTableViewCell: UITableViewCell {
    private let usernameLabel = UILabel()
    private let emailLabel = UILabel()
    private let adminLabel = UILabel()
    private let actionStackView = UIStackView()
    
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI() {
        // Username label
        usernameLabel.font = .systemFont(ofSize: 16, weight: .medium)
        usernameLabel.textColor = .label
        usernameLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(usernameLabel)
        
        // Email label
        emailLabel.font = .systemFont(ofSize: 14)
        emailLabel.textColor = .secondaryLabel
        emailLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(emailLabel)
        
        // Admin label
        adminLabel.font = .systemFont(ofSize: 12, weight: .semibold)
        adminLabel.textColor = .systemBlue
        adminLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(adminLabel)
        
        // Action buttons
        actionStackView.axis = .horizontal
        actionStackView.distribution = .fillEqually
        actionStackView.spacing = 8
        actionStackView.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(actionStackView)
        
        // Add placeholder buttons
        let toggleButton = createActionButton(title: "Toggle Admin", color: .systemOrange)
        let changePasswordButton = createActionButton(title: "Change Password", color: .systemBlue)
        let deleteButton = createActionButton(title: "Delete", color: .systemRed)
        
        actionStackView.addArrangedSubview(toggleButton)
        actionStackView.addArrangedSubview(changePasswordButton)
        actionStackView.addArrangedSubview(deleteButton)
        
        NSLayoutConstraint.activate([
            usernameLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 12),
            usernameLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            usernameLabel.trailingAnchor.constraint(equalTo: adminLabel.leadingAnchor, constant: -8),
            
            emailLabel.topAnchor.constraint(equalTo: usernameLabel.bottomAnchor, constant: 4),
            emailLabel.leadingAnchor.constraint(equalTo: usernameLabel.leadingAnchor),
            emailLabel.trailingAnchor.constraint(equalTo: actionStackView.leadingAnchor, constant: -8),
            
            adminLabel.topAnchor.constraint(equalTo: usernameLabel.topAnchor),
            adminLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            adminLabel.widthAnchor.constraint(equalToConstant: 60),
            
            actionStackView.topAnchor.constraint(equalTo: emailLabel.bottomAnchor, constant: 8),
            actionStackView.leadingAnchor.constraint(equalTo: emailLabel.leadingAnchor),
            actionStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            actionStackView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -12),
            actionStackView.heightAnchor.constraint(equalToConstant: 30)
        ])
    }
    
    private func createActionButton(title: String, color: UIColor) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle(title, for: .normal)
        button.setTitleColor(color, for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 10)
        button.backgroundColor = color.withAlphaComponent(0.1)
        button.layer.cornerRadius = 4
        return button
    }
    
    func configure(with user: User) {
        usernameLabel.text = user.username
        emailLabel.text = user.email
        adminLabel.text = user.isAdmin ? "Admin" : "User"
        adminLabel.textColor = user.isAdmin ? .systemBlue : .secondaryLabel
    }
} 