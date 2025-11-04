# frozen_string_literal: true

require 'faraday'
require 'json'
require 'logger'

module PayQI
  # Ruby API client for PayQI payment gateway
  # Similar to how Shopify has API clients for their services
  class Client
    attr_reader :api_url, :access_token, :logger

    def initialize(api_url: ENV['PAYQI_API_URL'] || 'http://localhost:8000', access_token: nil)
      @api_url = api_url
      @access_token = access_token
      @logger = Logger.new($stdout)

      @conn = Faraday.new(url: @api_url) do |faraday|
        faraday.request :json
        faraday.response :json, content_type: /\bjson$/
        faraday.response :logger, @logger if ENV['DEBUG']
        faraday.adapter Faraday.default_adapter
      end
    end

    # Authentication
    def register(email:, password:)
      response = @conn.post('/api/register') do |req|
        req.body = { email: email, password: password }
      end
      handle_response(response)
    end

    def login(email:, password:)
      response = @conn.post('/api/login') do |req|
        req.body = { email: email, password: password }
      end
      handle_response(response)
    end

    # Payments
    def create_payment(amount:, currency:, access_token:)
      response = @conn.post('/api/payments') do |req|
        req.headers['Authorization'] = "Bearer #{access_token}"
        req.body = { amount: amount, currency: currency }
      end
      handle_response(response)
    end

    def get_payment(payment_id:, access_token:)
      response = @conn.get("/api/payments/#{payment_id}") do |req|
        req.headers['Authorization'] = "Bearer #{access_token}"
      end
      handle_response(response)
    end

    def get_transactions(access_token:, skip: 0, limit: 100)
      response = @conn.get('/api/transactions') do |req|
        req.headers['Authorization'] = "Bearer #{access_token}"
        req.params = { skip: skip, limit: limit }
      end
      handle_response(response)
    end

    # Get current merchant info
    def get_merchant(access_token:)
      response = @conn.get('/api/me') do |req|
        req.headers['Authorization'] = "Bearer #{access_token}"
      end
      handle_response(response)
    end

    private

    def handle_response(response)
      parsed_body = normalize_body(response.body)

      if response.success?
        parsed_body
      else
        error_message = if parsed_body.is_a?(Hash)
                          parsed_body['detail'] || parsed_body['error'] || parsed_body['message'] || parsed_body.to_s
                        else
                          parsed_body.to_s
                        end
        raise APIError.new(error_message, response.status)
      end
    end

    def normalize_body(body)
      case body
      when String
        JSON.parse(body)
      when Hash, Array
        JSON.parse(JSON.generate(body))
      else
        body
      end
    rescue JSON::ParserError
      body
    end
  end

  # Custom error class (Shopify style)
  class APIError < StandardError
    attr_reader :status_code

    def initialize(message, status_code = nil)
      super(message)
      @status_code = status_code
    end
  end
end
