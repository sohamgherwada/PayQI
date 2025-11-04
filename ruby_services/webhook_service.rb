#!/usr/bin/env ruby
# frozen_string_literal: true

require 'sinatra'
require 'json'
require 'dotenv'
require 'faraday'
require 'logger'
require 'openssl'
require 'rack/protection'
require 'rack-timeout'

Dotenv.load

class WebhookService < Sinatra::Base
  configure do
    set :port, ENV.fetch('WEBHOOK_PORT', '4567').to_i
    set :bind, '0.0.0.0'
    set :logging, true
    set :dump_errors, true
    set :show_exceptions, false

    # Security settings
    set :protection, except: [:session_hijacking]
    use Rack::Protection::JsonCsrf
    use Rack::Timeout, service_timeout: 30
  end

  before do
    content_type 'application/json'
    @logger = Logger.new($stdout)
    @logger.level = Logger::INFO
    @logger.info("Request: #{request.request_method} #{request.path} from #{request.ip}")
  end

  # Health check endpoint
  get '/health' do
    { status: 'ok', service: 'webhook-processor', version: '1.0.0' }.to_json
  end

  # Process NOWPayments webhook
  post '/webhooks/nowpayments' do
    payload = request.body.read
    data = JSON.parse(payload)
    signature = request.env['HTTP_X_NOWPAYMENTS_SIG']

    @logger.info('Received NOWPayments webhook')

    # Verify webhook signature
    unless verify_nowpayments_signature(payload, signature)
      @logger.warn('Invalid webhook signature')
      halt 401, { error: 'Invalid signature' }.to_json
    end

    @logger.info("Processing payment webhook: #{data['payment_id']}")

    # Process the webhook asynchronously (in production, use background jobs)
    process_nowpayments_webhook(data)

    { status: 'ok', message: 'Webhook processed' }.to_json
  rescue JSON::ParserError => e
    @logger.error("Invalid JSON: #{e.message}")
    halt 400, { error: 'Invalid JSON' }.to_json
  rescue StandardError => e
    @logger.error("Error processing webhook: #{e.message}")
    halt 500, { error: 'Internal server error' }.to_json
  end

  # Process XRP payment webhook (from monitoring service)
  post '/webhooks/xrp' do
    payload = request.body.read
    data = JSON.parse(payload)

    @logger.info("Received XRP webhook for transaction: #{data['tx_hash']}")

    # Verify XRP transaction
    unless verify_xrp_transaction(data)
      @logger.warn('Invalid XRP transaction data')
      halt 400, { error: 'Invalid transaction data' }.to_json
    end

    # Process XRP payment
    process_xrp_payment(data)

    { status: 'ok', message: 'XRP payment processed' }.to_json
  rescue JSON::ParserError => e
    @logger.error("Invalid JSON: #{e.message}")
    halt 400, { error: 'Invalid JSON' }.to_json
  rescue StandardError => e
    @logger.error("Error processing XRP webhook: #{e.message}")
    halt 500, { error: 'Internal server error' }.to_json
  end

  private

  def verify_nowpayments_signature(payload, signature)
    secret = ENV.fetch('NOWPAYMENTS_IPN_SECRET', nil)
    return false unless signature && secret

    expected_signature = OpenSSL::HMAC.hexdigest(
      OpenSSL::Digest.new('sha512'),
      secret,
      payload
    )

    Rack::Utils.secure_compare(expected_signature, signature)
  end

  def verify_xrp_transaction(data)
    # Verify XRP transaction structure
    required_fields = %w[tx_hash destination_tag amount currency]
    required_fields.all? { |field| data.key?(field) } && data['currency'] == 'XRP'
  end

  def process_nowpayments_webhook(data)
    # Forward to Python API
    api_url = ENV.fetch('PYTHON_API_URL', 'http://backend:8000')

    conn = Faraday.new(url: api_url) do |faraday|
      faraday.request :json
      faraday.response :logger, @logger
      faraday.adapter Faraday.default_adapter
    end

    response = conn.post('/api/payments/webhook', data)

    if response.success?
      @logger.info('Successfully forwarded webhook to Python API')
    else
      @logger.error("Failed to forward webhook: #{response.status}")
      raise "API error: #{response.status}"
    end
  end

  def process_xrp_payment(data)
    # Forward XRP payment to Python API for processing
    api_url = ENV.fetch('PYTHON_API_URL', 'http://backend:8000')

    conn = Faraday.new(url: api_url) do |faraday|
      faraday.request :json
      faraday.response :logger, @logger
      faraday.adapter Faraday.default_adapter
    end

    webhook_data = {
      provider: 'xrp',
      tx_hash: data['tx_hash'],
      destination_tag: data['destination_tag'],
      amount: data['amount'],
      currency: data['currency'],
      timestamp: Time.now.utc.iso8601
    }

    response = conn.post('/api/payments/webhook', webhook_data)

    if response.success?
      @logger.info("Successfully processed XRP payment: #{data['tx_hash']}")
    else
      @logger.error("Failed to process XRP payment: #{response.status}")
      raise "API error: #{response.status}"
    end
  end
end

WebhookService.run! if __FILE__ == $PROGRAM_NAME
