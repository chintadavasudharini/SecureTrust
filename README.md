# 🛡️ SecureTrust — Enterprise-Grade Fintech Prototype

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Deployment](https://img.shields.io/badge/Deployed-Render-430098?style=for-the-badge&logo=render&logoColor=white)](https://securetrust.onrender.com)

> **SecureTrust** is a sophisticated fintech simulation platform designed to demonstrate modern banking workflows, robust Role-Based Access Control (RBAC), and multi-channel financial transaction processing.
>
> 🚀 **[View the Development Roadmap](ROADMAP.md)**

---

## 💎 The Vision
SecureTrust bridges the gap between complex banking legacy systems and modern, intuitive fintech experiences. It serves as a blueprint for high-security financial applications, prioritizing **atomic transactions**, **granular administrative oversight**, and **seamless user onboarding**.

## 🚀 Key Modules

### 👤 Customer Experience (Retail Banking)
*   **Omni-channel Transfers**: Unified interface for Internal Transfers, Other Bank (NEFT/IMPS), and simulated UPI payments.
*   **Liquidity Management**: Real-time deposit/withdrawal engine with minimum balance enforcement (₹500) and transaction limits.
*   **Asset Management**: Integrated Fixed Deposit (FD) and Loan application workflows.
*   **Card Command Center**: End-to-end card lifecycle management including PIN rotation and virtual card viewing.
*   **Live Audit Trail**: Chronological account statements with detailed transaction metadata.

### 🏢 Administrative Governance (RBAC)
SecureTrust implements a strict hierarchical permission model:
*   **Super Administrator**: The root authority. Exclusive permissions for administrator enrollment and system-wide state management.
*   **Auditors**: Read-only access to transaction logs and user directories for compliance monitoring.
*   **Transaction Managers**: Specialized oversight for financial flows and liquidity reporting.
*   **Onboarding Officers**: Dedicated workflows for customer KYC and account initialization.

---

## 🛠️ Technical Architecture

### Stack
- **Engine**: Flask 3.0 (WSGI compliant)
- **Templating**: Jinja2 with modular macro structures
- **Session Management**: Secure, encrypted cookie-based sessions with a 10-minute sliding expiration.
- **Data Layer**: High-performance in-memory state (Optimized for demonstration environments).

### Security Implementations
- **Session Pinning**: `permanent_session_lifetime` enforced at the middleware level.
- **RBAC Middleware**: Custom route decorators/checks to ensure zero-leakage of admin endpoints.
- **Input Sanitization**: Strict validation on financial amounts and account identifiers.
- **Integrity Constraints**: Multi-step verification for account balance mutations.

---

## ⚙️ Quick Start

### Prerequisites
- Python 3.10+
- Virtualenv / Pipenv

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/chintadavasudharini/SecureTrust.git
   cd SecureTrust
   ```

2. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Execution**
   ```bash
   python app.py
   ```
   *The application will be available at `http://127.0.0.1:5000`*

---

## 📑 Roadmap & Future Enhancements
- [ ] **Persistent Storage**: Migration from in-memory `dict` to PostgreSQL with SQLAlchemy ORM.
- [ ] **MFA Integration**: TOTP-based Multi-Factor Authentication for Admin logins.
- [ ] **Real-time Notifications**: Webhook integration for transaction alerts via Twilio/SendGrid.
- [ ] **API Layer**: Transitioning to a decoupled React frontend with a Flask-RESTful API.

---

## 🤝 Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.

## ✉️ Contact
**Chintada Vasudharini**
- **LinkedIn**: [chintada-vasudharini](https://www.linkedin.com/in/chintada-vasudharini-nov21/)
- **Portfolio**: [portfolio-lime-tau-36.vercel.app](https://portfolio-lime-tau-36.vercel.app/)
- **GitHub**: [chintadavasudharini](https://github.com/chintadavasudharini)
- **Email**: [chintadavasudharini@gmail.com](mailto:chintadavasudharini@gmail.com)

Project Link: [https://github.com/chintadavasudharini/SecureTrust](https://github.com/chintadavasudharini/SecureTrust)

---
*Developed with ❤️ by Chintada Vasudharini*

*Disclaimer: This is a simulation project. It is not intended for real financial transactions. Use for educational and demonstration purposes only.*
