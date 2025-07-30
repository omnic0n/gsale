import UIKit

class DashboardViewController: UIViewController {
    
    // MARK: - UI Elements
    private let scrollView: UIScrollView = {
        let scrollView = UIScrollView()
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        return scrollView
    }()
    
    private let contentView: UIView = {
        let view = UIView()
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private let welcomeLabel: UILabel = {
        let label = UILabel()
        label.font = UIFont.systemFont(ofSize: 24, weight: .bold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let statsStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let profitCard = DashboardCard(title: "Total Profit", value: "$0", icon: "dollarsign.circle.fill", color: .systemGreen)
    private let salesCard = DashboardCard(title: "Total Sales", value: "0", icon: "cart.fill", color: .systemBlue)
    private let purchasesCard = DashboardCard(title: "Total Purchases", value: "0", icon: "bag.fill", color: .systemOrange)
    
    private let menuStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .vertical
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let itemsButton = MenuButton(title: "Items", subtitle: "Manage your inventory", icon: "cube.fill", color: .systemBlue)
    private let groupsButton = MenuButton(title: "Groups", subtitle: "Organize items", icon: "folder.fill", color: .systemGreen)
    private let expensesButton = MenuButton(title: "Expenses", subtitle: "Track costs", icon: "creditcard.fill", color: .systemRed)
    private let reportsButton = MenuButton(title: "Reports", subtitle: "View analytics", icon: "chart.bar.fill", color: .systemPurple)
    private let adminButton = MenuButton(title: "Admin", subtitle: "User management", icon: "person.2.fill", color: .systemIndigo)
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
        setupActions()
        setupNavigationBar()
        loadDashboardData()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        loadDashboardData()
    }
    
    // MARK: - UI Setup
    private func setupUI() {
        view.backgroundColor = .systemBackground
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(welcomeLabel)
        contentView.addSubview(statsStackView)
        contentView.addSubview(menuStackView)
        
        statsStackView.addArrangedSubview(profitCard)
        statsStackView.addArrangedSubview(salesCard)
        statsStackView.addArrangedSubview(purchasesCard)
        
        menuStackView.addArrangedSubview(itemsButton)
        menuStackView.addArrangedSubview(groupsButton)
        menuStackView.addArrangedSubview(expensesButton)
        menuStackView.addArrangedSubview(reportsButton)
        
        // Only show admin button if user is admin
        if UserManager.shared.isAdmin() {
            menuStackView.addArrangedSubview(adminButton)
        }
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Scroll view
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            // Content view
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            
            // Welcome label
            welcomeLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 20),
            welcomeLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            welcomeLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            // Stats stack view
            statsStackView.topAnchor.constraint(equalTo: welcomeLabel.bottomAnchor, constant: 30),
            statsStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            statsStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            // Menu stack view
            menuStackView.topAnchor.constraint(equalTo: statsStackView.bottomAnchor, constant: 40),
            menuStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            menuStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            menuStackView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -20)
        ])
    }
    
    private func setupActions() {
        itemsButton.addTarget(self, action: #selector(itemsButtonTapped), for: .touchUpInside)
        groupsButton.addTarget(self, action: #selector(groupsButtonTapped), for: .touchUpInside)
        expensesButton.addTarget(self, action: #selector(expensesButtonTapped), for: .touchUpInside)
        reportsButton.addTarget(self, action: #selector(reportsButtonTapped), for: .touchUpInside)
        adminButton.addTarget(self, action: #selector(adminButtonTapped), for: .touchUpInside)
    }
    
    private func setupNavigationBar() {
        title = "Dashboard"
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            title: "Logout",
            style: .plain,
            target: self,
            action: #selector(logoutButtonTapped)
        )
        
        welcomeLabel.text = "Welcome, \(UserManager.shared.getUsername() ?? "User")!"
    }
    
    // MARK: - Data Loading
    private func loadDashboardData() {
        NetworkManager.shared.getDashboardData { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let data):
                    self?.updateDashboard(with: data)
                case .failure(let error):
                    print("Error loading dashboard data: \(error)")
                }
            }
        }
    }
    
    private func updateDashboard(with data: DashboardData) {
        profitCard.updateValue("$\(String(format: "%.2f", data.totalProfit))")
        salesCard.updateValue("\(data.totalSales)")
        purchasesCard.updateValue("\(data.totalPurchases)")
    }
    
    // MARK: - Actions
    @objc private func itemsButtonTapped() {
        let itemsVC = ItemsViewController()
        navigationController?.pushViewController(itemsVC, animated: true)
    }
    
    @objc private func groupsButtonTapped() {
        let groupsVC = GroupsViewController()
        navigationController?.pushViewController(groupsVC, animated: true)
    }
    
    @objc private func expensesButtonTapped() {
        let expensesVC = ExpensesViewController()
        navigationController?.pushViewController(expensesVC, animated: true)
    }
    
    @objc private func reportsButtonTapped() {
        let reportsVC = ReportsViewController()
        navigationController?.pushViewController(reportsVC, animated: true)
    }
    
    @objc private func adminButtonTapped() {
        let adminVC = AdminViewController()
        navigationController?.pushViewController(adminVC, animated: true)
    }
    
    @objc private func logoutButtonTapped() {
        let alert = UIAlertController(title: "Logout", message: "Are you sure you want to logout?", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Logout", style: .destructive) { _ in
            UserManager.shared.logout()
            self.dismiss(animated: true)
        })
        present(alert, animated: true)
    }
}

// MARK: - Dashboard Card
class DashboardCard: UIView {
    private let iconImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.font = UIFont.systemFont(ofSize: 12, weight: .medium)
        label.textColor = .secondaryLabel
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let valueLabel: UILabel = {
        let label = UILabel()
        label.font = UIFont.systemFont(ofSize: 20, weight: .bold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    init(title: String, value: String, icon: String, color: UIColor) {
        super.init(frame: .zero)
        setupUI(title: title, value: value, icon: icon, color: color)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI(title: String, value: String, icon: String, color: UIColor) {
        backgroundColor = .secondarySystemBackground
        layer.cornerRadius = 12
        
        addSubview(iconImageView)
        addSubview(titleLabel)
        addSubview(valueLabel)
        
        iconImageView.image = UIImage(systemName: icon)
        iconImageView.tintColor = color
        titleLabel.text = title
        valueLabel.text = value
        valueLabel.textColor = color
        
        NSLayoutConstraint.activate([
            iconImageView.topAnchor.constraint(equalTo: topAnchor, constant: 12),
            iconImageView.centerXAnchor.constraint(equalTo: centerXAnchor),
            iconImageView.widthAnchor.constraint(equalToConstant: 24),
            iconImageView.heightAnchor.constraint(equalToConstant: 24),
            
            titleLabel.topAnchor.constraint(equalTo: iconImageView.bottomAnchor, constant: 8),
            titleLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 8),
            titleLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -8),
            
            valueLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 4),
            valueLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 8),
            valueLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -8),
            valueLabel.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -12)
        ])
    }
    
    func updateValue(_ value: String) {
        valueLabel.text = value
    }
}

// MARK: - Menu Button
class MenuButton: UIButton {
    private let iconImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let subtitleLabel: UILabel = {
        let label = UILabel()
        label.font = UIFont.systemFont(ofSize: 14, weight: .regular)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    init(title: String, subtitle: String, icon: String, color: UIColor) {
        super.init(frame: .zero)
        setupUI(title: title, subtitle: subtitle, icon: icon, color: color)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI(title: String, subtitle: String, icon: String, color: UIColor) {
        backgroundColor = .secondarySystemBackground
        layer.cornerRadius = 12
        
        addSubview(iconImageView)
        addSubview(titleLabel)
        addSubview(subtitleLabel)
        
        iconImageView.image = UIImage(systemName: icon)
        iconImageView.tintColor = color
        titleLabel.text = title
        subtitleLabel.text = subtitle
        
        NSLayoutConstraint.activate([
            iconImageView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            iconImageView.centerYAnchor.constraint(equalTo: centerYAnchor),
            iconImageView.widthAnchor.constraint(equalToConstant: 24),
            iconImageView.heightAnchor.constraint(equalToConstant: 24),
            
            titleLabel.leadingAnchor.constraint(equalTo: iconImageView.trailingAnchor, constant: 16),
            titleLabel.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            titleLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            
            subtitleLabel.leadingAnchor.constraint(equalTo: titleLabel.leadingAnchor),
            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 4),
            subtitleLabel.trailingAnchor.constraint(equalTo: titleLabel.trailingAnchor),
            subtitleLabel.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16)
        ])
        
        heightAnchor.constraint(equalToConstant: 80).isActive = true
    }
} 