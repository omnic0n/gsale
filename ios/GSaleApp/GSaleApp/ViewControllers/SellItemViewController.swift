import UIKit

class SellItemViewController: UIViewController {

    private let scrollView = UIScrollView()
    private let contentView = UIView()

    private let titleLabel = UILabel()
    private let idLabel = UILabel()
    private let idValueLabel = UILabel()
    private let priceTextField = UITextField()
    private let dateTextField = UITextField()
    private let shippingTextField = UITextField()
    private let submitButton = UIButton(type: .system)
    private let loadingIndicator = UIActivityIndicatorView(style: .large)

    private let itemId: String
    private let itemName: String
    private let groupId: String

    init(itemId: String, itemName: String, groupId: String) {
        self.itemId = itemId
        self.itemName = itemName
        self.groupId = groupId
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupHomeButton()
    }

    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Sell Item"

        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)

        titleLabel.text = itemName
        titleLabel.font = UIFont.systemFont(ofSize: 22, weight: .bold)
        titleLabel.translatesAutoresizingMaskIntoConstraints = false

        idLabel.text = "ID:"
        idLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        idLabel.translatesAutoresizingMaskIntoConstraints = false

        idValueLabel.text = itemId
        idValueLabel.font = UIFont.systemFont(ofSize: 16)
        idValueLabel.textColor = .secondaryLabel
        idValueLabel.numberOfLines = 0
        idValueLabel.translatesAutoresizingMaskIntoConstraints = false

        priceTextField.placeholder = "Sold Price (e.g., 25.00)"
        priceTextField.keyboardType = .decimalPad
        priceTextField.borderStyle = .roundedRect
        priceTextField.translatesAutoresizingMaskIntoConstraints = false

        dateTextField.placeholder = "Sale Date (YYYY-MM-DD)"
        dateTextField.text = todayString()
        dateTextField.keyboardType = .numbersAndPunctuation
        dateTextField.borderStyle = .roundedRect
        dateTextField.translatesAutoresizingMaskIntoConstraints = false

        shippingTextField.placeholder = "Shipping Fee (e.g., 3.50)"
        shippingTextField.keyboardType = .decimalPad
        shippingTextField.borderStyle = .roundedRect
        shippingTextField.translatesAutoresizingMaskIntoConstraints = false

        submitButton.setTitle("Save", for: .normal)
        submitButton.setTitleColor(.white, for: .normal)
        submitButton.backgroundColor = .systemGreen
        submitButton.layer.cornerRadius = 10
        submitButton.titleLabel?.font = UIFont.systemFont(ofSize: 17, weight: .semibold)
        submitButton.contentEdgeInsets = UIEdgeInsets(top: 12, left: 20, bottom: 12, right: 20)
        submitButton.translatesAutoresizingMaskIntoConstraints = false
        submitButton.addTarget(self, action: #selector(submitTapped), for: .touchUpInside)

        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        loadingIndicator.hidesWhenStopped = true

        contentView.addSubview(titleLabel)
        contentView.addSubview(idLabel)
        contentView.addSubview(idValueLabel)
        contentView.addSubview(priceTextField)
        contentView.addSubview(dateTextField)
        contentView.addSubview(shippingTextField)
        contentView.addSubview(submitButton)
        contentView.addSubview(loadingIndicator)

        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),

            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor, constant: 16),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor, constant: -16),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor, constant: -32),

            titleLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 24),
            titleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            titleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),

            idLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 24),
            idLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            idValueLabel.centerYAnchor.constraint(equalTo: idLabel.centerYAnchor),
            idValueLabel.leadingAnchor.constraint(equalTo: idLabel.trailingAnchor, constant: 8),
            idValueLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),

            priceTextField.topAnchor.constraint(equalTo: idLabel.bottomAnchor, constant: 24),
            priceTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            priceTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),

            dateTextField.topAnchor.constraint(equalTo: priceTextField.bottomAnchor, constant: 16),
            dateTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            dateTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),

            shippingTextField.topAnchor.constraint(equalTo: dateTextField.bottomAnchor, constant: 16),
            shippingTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            shippingTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),

            submitButton.topAnchor.constraint(equalTo: shippingTextField.bottomAnchor, constant: 24),
            submitButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            submitButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),
            submitButton.bottomAnchor.constraint(lessThanOrEqualTo: contentView.bottomAnchor, constant: -24),

            loadingIndicator.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: submitButton.centerYAnchor)
        ])
    }

    private func setupHomeButton() {
        let homeImage = UIImage(systemName: "house.fill")
        let homeButton = UIBarButtonItem(image: homeImage, style: .plain, target: self, action: #selector(goHome))
        navigationItem.rightBarButtonItem = homeButton
    }

    @objc private func goHome() {
        navigationController?.popToRootViewController(animated: true)
    }

    private func todayString() -> String {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd"
        return df.string(from: Date())
    }

    @objc private func submitTapped() {
        let date = dateTextField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let price = priceTextField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? "0"
        let shipping = shippingTextField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? "0"

        if date.isEmpty || price.isEmpty {
            showAlert(title: "Missing Info", message: "Please enter date and price.")
            return
        }

        loadingIndicator.startAnimating()
        submitButton.isEnabled = false

        Task {
            do {
                try await NetworkManager.shared.markItemSold(itemId: itemId, soldDate: date, price: price, shippingFee: shipping)
                // After marking as sold, navigate to the group's detail page
                let groupDetail = try await NetworkManager.shared.getGroupDetails(groupId: self.groupId)
                await MainActor.run {
                    self.loadingIndicator.stopAnimating()
                    self.submitButton.isEnabled = true
                    let vc = GroupDetailViewController(groupDetail: groupDetail)
                    self.navigationController?.pushViewController(vc, animated: true)
                }
            } catch {
                await MainActor.run {
                    self.loadingIndicator.stopAnimating()
                    self.submitButton.isEnabled = true
                    self.showAlert(title: "Error", message: "Failed to mark item sold. Please try again.")
                }
            }
        }
    }

    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}


