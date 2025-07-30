import UIKit

class GroupDetailViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let headerView = UIView()
    private let nameLabel = UILabel()
    private let dateLabel = UILabel()
    private let priceLabel = UILabel()
    private let statsView = UIView()
    private let totalItemsLabel = UILabel()
    private let soldItemsLabel = UILabel()
    private let soldPriceLabel = UILabel()
    
    private let itemsTableView = UITableView()
    private let itemsLabel = UILabel()
    
    private let groupDetail: GroupDetail
    
    init(groupDetail: GroupDetail) {
        self.groupDetail = groupDetail
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupData()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Group Details"
        
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        // Header setup
        headerView.backgroundColor = .secondarySystemBackground
        headerView.layer.cornerRadius = 12
        headerView.translatesAutoresizingMaskIntoConstraints = false
        
        nameLabel.font = UIFont.systemFont(ofSize: 24, weight: .bold)
        nameLabel.textColor = .label
        nameLabel.translatesAutoresizingMaskIntoConstraints = false
        
        dateLabel.font = UIFont.systemFont(ofSize: 16)
        dateLabel.textColor = .secondaryLabel
        dateLabel.translatesAutoresizingMaskIntoConstraints = false
        
        priceLabel.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        priceLabel.textColor = .systemBlue
        priceLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Stats setup
        statsView.backgroundColor = .tertiarySystemBackground
        statsView.layer.cornerRadius = 8
        statsView.translatesAutoresizingMaskIntoConstraints = false
        
        totalItemsLabel.font = UIFont.systemFont(ofSize: 14)
        totalItemsLabel.textColor = .secondaryLabel
        totalItemsLabel.translatesAutoresizingMaskIntoConstraints = false
        
        soldItemsLabel.font = UIFont.systemFont(ofSize: 14)
        soldItemsLabel.textColor = .secondaryLabel
        soldItemsLabel.translatesAutoresizingMaskIntoConstraints = false
        
        soldPriceLabel.font = UIFont.systemFont(ofSize: 14)
        soldPriceLabel.textColor = .secondaryLabel
        soldPriceLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Items setup
        itemsLabel.text = "Items"
        itemsLabel.font = UIFont.systemFont(ofSize: 20, weight: .semibold)
        itemsLabel.textColor = .label
        itemsLabel.translatesAutoresizingMaskIntoConstraints = false
        
        itemsTableView.delegate = self
        itemsTableView.dataSource = self
        itemsTableView.register(UITableViewCell.self, forCellReuseIdentifier: "ItemCell")
        itemsTableView.translatesAutoresizingMaskIntoConstraints = false
        itemsTableView.isScrollEnabled = false
        
        // Add subviews
        headerView.addSubview(nameLabel)
        headerView.addSubview(dateLabel)
        headerView.addSubview(priceLabel)
        headerView.addSubview(statsView)
        
        statsView.addSubview(totalItemsLabel)
        statsView.addSubview(soldItemsLabel)
        statsView.addSubview(soldPriceLabel)
        
        contentView.addSubview(headerView)
        contentView.addSubview(itemsLabel)
        contentView.addSubview(itemsTableView)
        
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
            
            headerView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 20),
            headerView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            headerView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            nameLabel.topAnchor.constraint(equalTo: headerView.topAnchor, constant: 20),
            nameLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            nameLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            
            dateLabel.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 8),
            dateLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            dateLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            
            priceLabel.topAnchor.constraint(equalTo: dateLabel.bottomAnchor, constant: 8),
            priceLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            priceLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            
            statsView.topAnchor.constraint(equalTo: priceLabel.bottomAnchor, constant: 16),
            statsView.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            statsView.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            statsView.bottomAnchor.constraint(equalTo: headerView.bottomAnchor, constant: -20),
            statsView.heightAnchor.constraint(equalToConstant: 80),
            
            totalItemsLabel.topAnchor.constraint(equalTo: statsView.topAnchor, constant: 16),
            totalItemsLabel.leadingAnchor.constraint(equalTo: statsView.leadingAnchor, constant: 16),
            
            soldItemsLabel.topAnchor.constraint(equalTo: totalItemsLabel.bottomAnchor, constant: 8),
            soldItemsLabel.leadingAnchor.constraint(equalTo: statsView.leadingAnchor, constant: 16),
            
            soldPriceLabel.topAnchor.constraint(equalTo: soldItemsLabel.bottomAnchor, constant: 8),
            soldPriceLabel.leadingAnchor.constraint(equalTo: statsView.leadingAnchor, constant: 16),
            
            itemsLabel.topAnchor.constraint(equalTo: headerView.bottomAnchor, constant: 30),
            itemsLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            itemsLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            itemsTableView.topAnchor.constraint(equalTo: itemsLabel.bottomAnchor, constant: 16),
            itemsTableView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            itemsTableView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            itemsTableView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -20),
            itemsTableView.heightAnchor.constraint(equalToConstant: CGFloat(groupDetail.items.count * 60))
        ])
    }
    
    private func setupData() {
        nameLabel.text = groupDetail.name
        dateLabel.text = "Date: \(groupDetail.date)"
        priceLabel.text = "Price: $\(String(format: "%.2f", groupDetail.price))"
        
        totalItemsLabel.text = "Total Items: \(groupDetail.totalItems)"
        soldItemsLabel.text = "Sold Items: \(groupDetail.totalSoldItems)"
        soldPriceLabel.text = "Sold Price: $\(String(format: "%.2f", groupDetail.soldPrice))"
    }
}

extension GroupDetailViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return groupDetail.items.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ItemCell", for: indexPath)
        let item = groupDetail.items[indexPath.row]
        
        cell.textLabel?.text = item.name
        cell.detailTextLabel?.text = "$\(String(format: "%.2f", item.price))"
        
        if item.sold {
            cell.backgroundColor = .systemGreen.withAlphaComponent(0.1)
            cell.textLabel?.textColor = .systemGreen
        } else {
            cell.backgroundColor = .systemBackground
            cell.textLabel?.textColor = .label
        }
        
        return cell
    }
}

extension GroupDetailViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        
        let item = groupDetail.items[indexPath.row]
        let status = item.sold ? "Sold" : "Available"
        let alert = UIAlertController(title: item.name, message: "Price: $\(String(format: "%.2f", item.price))\nStatus: \(status)", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
} 