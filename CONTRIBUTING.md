# Contributing to CyberGuard IDS/IPS Platform

Thank you for your interest in contributing to the CyberGuard IDS/IPS Platform! This document provides guidelines for contributing to this cybersecurity project.

## 🛡️ Security First

This is a cybersecurity project, so security considerations are paramount:

- **Never commit sensitive data** (API keys, passwords, certificates)
- **Test security features thoroughly** before submitting
- **Report security vulnerabilities** privately via email
- **Follow secure coding practices** in all contributions

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL
- Redis
- Docker (optional)

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/cyberguard-ids-ips.git
cd cyberguard-ids-ips

# Run setup
./setup.sh

# Start development environment
./start.sh
```

## 📋 Development Workflow

### 1. Fork and Clone
1. Fork the repository on GitHub
2. Clone your fork locally
3. Add upstream remote: `git remote add upstream https://github.com/original/cyberguard-ids-ips.git`

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Development Guidelines

#### Backend Development (`/backend/`)
- Use **FastAPI** for API endpoints
- Follow **async/await** patterns
- Add **type hints** to all functions
- Use **SQLAlchemy** for database operations
- Implement **proper error handling**
- Add **logging** for debugging

#### Frontend Development (`/frontend/`)
- Use **Next.js 13+** with app directory
- Follow **React** best practices
- Use **TypeScript** for type safety
- Implement **responsive design**
- Add **loading states** and **error handling**
- Use **Tailwind CSS** for styling

#### Machine Learning (`/ml-iot/`)
- Document **model performance** metrics
- Include **training scripts** and **data preprocessing**
- Use **version control** for model files
- Add **model validation** and **testing**

### 4. Code Quality Standards

#### Python Code Style
```python
# Use type hints
async def detect_threat(packet_data: dict) -> ThreatResult:
    """Detect threats in network packet data."""
    pass

# Use proper error handling
try:
    result = await process_packet(data)
except Exception as e:
    logger.error(f"Packet processing failed: {e}")
    raise
```

#### TypeScript Code Style
```typescript
// Use proper interfaces
interface ThreatAlert {
  id: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

// Use async/await
const fetchThreats = async (): Promise<ThreatAlert[]> => {
  try {
    const response = await apiClient.getThreats();
    return response.data;
  } catch (error) {
    console.error('Failed to fetch threats:', error);
    throw error;
  }
};
```

### 5. Testing Requirements

#### Backend Tests
```bash
cd backend/tests
python test_complete_system.py
```

#### Frontend Tests
```bash
cd frontend
npm test
```

#### Integration Tests
```bash
./scripts/quick_test_all.sh
```

### 6. Documentation

- Update **README.md** for new features
- Add **docstrings** to Python functions
- Include **JSDoc comments** for TypeScript
- Update **API documentation** for new endpoints
- Add **examples** for complex features

## 🎯 Contribution Types

### Bug Fixes
- Include **reproduction steps**
- Add **test cases** for the fix
- Reference **issue number** in commit message

### New Features
- Discuss **feature proposal** in issues first
- Include **comprehensive tests**
- Update **documentation**
- Add **configuration options** if needed

### Security Improvements
- Follow **responsible disclosure**
- Include **security impact** assessment
- Add **mitigation strategies**
- Update **security documentation**

### Performance Optimizations
- Include **benchmarks** before/after
- Document **performance impact**
- Add **monitoring** for new metrics

## 📝 Commit Guidelines

### Commit Message Format
```
type(scope): brief description

Detailed explanation of changes made.

Fixes #issue-number
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `security`: Security improvements

### Examples
```
feat(backend): add threat intelligence API integration

- Integrate with VirusTotal API for IP reputation
- Add caching for threat intelligence data
- Include rate limiting for external API calls

Fixes #123
```

## 🧪 Testing Guidelines

### Test Categories
1. **Unit Tests**: Individual function testing
2. **Integration Tests**: Component interaction testing
3. **Security Tests**: Vulnerability and penetration testing
4. **Performance Tests**: Load and stress testing
5. **End-to-End Tests**: Complete workflow testing

### Test Requirements
- **Minimum 80% code coverage**
- **All security features tested**
- **Performance benchmarks included**
- **Error scenarios covered**

## 🔍 Code Review Process

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Breaking changes documented

### Review Timeline
- **Initial review**: Within 48 hours
- **Follow-up reviews**: Within 24 hours
- **Final approval**: Within 72 hours

## 🚨 Security Guidelines

### Secure Coding Practices
- **Input validation** on all user inputs
- **SQL injection prevention** with parameterized queries
- **XSS prevention** with proper escaping
- **Authentication** and **authorization** checks
- **Rate limiting** on API endpoints
- **Logging** without sensitive data

### Security Testing
- **Static code analysis**
- **Dependency vulnerability scanning**
- **Penetration testing** for new features
- **Security code review**

## 📊 Performance Guidelines

### Backend Performance
- **Database query optimization**
- **Async processing** for I/O operations
- **Caching** for frequently accessed data
- **Connection pooling** for databases

### Frontend Performance
- **Code splitting** for large bundles
- **Lazy loading** for components
- **Image optimization**
- **Caching strategies**

## 🤝 Community Guidelines

### Communication
- Be **respectful** and **professional**
- Use **clear** and **concise** language
- **Help others** learn and contribute
- **Share knowledge** and **best practices**

### Issue Reporting
- Use **issue templates**
- Include **reproduction steps**
- Provide **system information**
- Add **relevant logs** and **screenshots**

## 📞 Getting Help

### Resources
- **Documentation**: `/docs` directory
- **Examples**: `/backend/tests` and `/frontend/tests`
- **Scripts**: `/scripts` directory for automation
- **Issues**: GitHub Issues for questions and bugs

### Contact
- **General questions**: GitHub Discussions
- **Bug reports**: GitHub Issues
- **Security issues**: Email (private)
- **Feature requests**: GitHub Issues with enhancement label

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for contributing to cybersecurity! 🛡️
