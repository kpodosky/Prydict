## Prydict - Cryptocurrency Fee Predictor

A real-time cryptocurrency transaction fee predictor and mainnet tracker built with Go.

 ## Features

- Real-time fee predictions for:
  - Bitcoin (BTC)
  - Ethereum (ETH)
  - USDC
  - USDT
- Transaction size optimization
- Whale transaction monitoring
- Simple and intuitive interface

## Prerequisites

- Go 1.21 or higher
- Docker (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/prydict.git
cd prydict
```

2. Build and run locally:
```bash
go mod tidy
go run main.go
```

3. Or using Docker:
```bash
docker build -t prydict .
docker run -p 8080:8080 prydict
```

## Project Structure

prydict/
├── main.go              # Main application entry
├── static/              # Static assets
│   └── js/
│       └── main.js      # JavaScript code
├── templates/           # HTML templates
│   └── index.html
├── Dockerfile          # Docker configuration
├── go.mod             # Go module file
└── README.md          # This file


## API Endpoints

- `GET /` - Home page
- `POST /predict` - Fee prediction endpoint

## Deployment

### Render Deployment

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Use the following settings:
   - Build Command: `go build -o app`
   - Start Command: `./app`

## Environment Variables

- `PORT` - Server port (default: 8080)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Go
- Powered by coindesk
- Inspired by the need for better fee prediction in crypto transactions

