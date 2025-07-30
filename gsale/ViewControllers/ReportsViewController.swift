import UIKit

class ReportsViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    private let refreshControl = UIRefreshControl()
    
    private let profitCard = ReportCard()
    private let salesCard = ReportCard()
    private let purchasesCard = ReportCard()
    private let expensesCard = ReportCard()
    
    private var reportsData: ReportsData?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
        setupActions()
        setupNavigationBar()
        loadReports()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Reports"
        
        // Scroll view
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.backgroundColor = .systemBackground
        view.addSubview(scrollView)
        
        // Content view
        contentView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(contentView)
        
        // Report cards
        profitCard.configure(title: "Total Profit", value: "$0.00", color: .systemGreen)
        salesCard.configure(title: "Total Sales", value: "$0.00", color: .systemBlue)
        purchasesCard.configure(title: "Total Purchases", value: "$0.00", color: .systemOrange)
        expensesCard.configure(title: "Total Expenses", value: "$0.00", color: .systemRed)
        
        contentView.addSubview(profitCard)
        contentView.addSubview(salesCard)
        contentView.addSubview(purchasesCard)
        contentView.addSubview(expensesCard)
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
            
            profitCard.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 16),
            profitCard.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            profitCard.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            profitCard.heightAnchor.constraint(equalToConstant: 100),
            
            salesCard.topAnchor.constraint(equalTo: profitCard.bottomAnchor, constant: 16),
            salesCard.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            salesCard.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            salesCard.heightAnchor.constraint(equalToConstant: 100),
            
            purchasesCard.topAnchor.constraint(equalTo: salesCard.bottomAnchor, constant: 16),
            purchasesCard.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            purchasesCard.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            purchasesCard.heightAnchor.constraint(equalToConstant: 100),
            
            expensesCard.topAnchor.constraint(equalTo: purchasesCard.bottomAnchor, constant: 16),
            expensesCard.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            expensesCard.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            expensesCard.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -16),
            expensesCard.heightAnchor.constraint(equalToConstant: 100)
        ])
    }
    
    private func setupActions() {
        scrollView.refreshControl = refreshControl
        refreshControl.addTarget(self, action: #selector(refreshData), for: .valueChanged)
    }
    
    private func setupNavigationBar() {
        navigationItem.leftBarButtonItem = UIBarButtonItem(title: "Back", style: .plain, target: self, action: #selector(backButtonTapped))
    }
    
    private func loadReports() {
        NetworkManager.shared.getReports { [weak self] result in
            DispatchQueue.main.async {
                self?.refreshControl.endRefreshing()
                
                switch result {
                case .success(let reportsData):
                    self?.reportsData = reportsData
                    self?.updateReports(with: reportsData)
                case .failure(let error):
                    self?.showAlert(title: "Error", message: error.localizedDescription)
                }
            }
        }
    }
    
    private func updateReports(with data: ReportsData) {
        profitCard.updateValue(String(format: "$%.2f", data.totalProfit))
        salesCard.updateValue(String(format: "$%.2f", data.totalSales))
        purchasesCard.updateValue(String(format: "$%.2f", data.totalPurchases))
        expensesCard.updateValue(String(format: "$%.2f", data.totalExpenses))
    }
    
    @objc private func refreshData() {
        loadReports()
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

class ReportCard: UIView {
    private let titleLabel = UILabel()
    private let valueLabel = UILabel()
    private var cardColor: UIColor = .systemBlue
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI() {
        backgroundColor = .systemBackground
        layer.cornerRadius = 12
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0, height: 2)
        layer.shadowRadius = 4
        layer.shadowOpacity = 0.1
        
        titleLabel.font = .systemFont(ofSize: 16, weight: .medium)
        titleLabel.textColor = .secondaryLabel
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        addSubview(titleLabel)
        
        valueLabel.font = .systemFont(ofSize: 24, weight: .bold)
        valueLabel.textColor = .label
        valueLabel.translatesAutoresizingMaskIntoConstraints = false
        addSubview(valueLabel)
        
        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            titleLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            titleLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            
            valueLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            valueLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            valueLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            valueLabel.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16)
        ])
    }
    
    func configure(title: String, value: String, color: UIColor) {
        titleLabel.text = title
        valueLabel.text = value
        cardColor = color
        valueLabel.textColor = color
    }
    
    func updateValue(_ value: String) {
        valueLabel.text = value
    }
} 