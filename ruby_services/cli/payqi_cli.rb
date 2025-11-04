#!/usr/bin/env ruby
# frozen_string_literal: true

require 'thor'
require 'json'
require 'dotenv'
require_relative '../lib/payqi_client'

# Add lib to path for standalone execution
lib_path = "#{File.dirname(__FILE__)}/../lib"
$LOAD_PATH.unshift(lib_path) unless $LOAD_PATH.include?(lib_path)

Dotenv.load

# CLI tool for PayQI - demonstrating Ruby skills for Shopify
# Similar to Shopify CLI tools
class PayQICLI < Thor
  desc 'register EMAIL PASSWORD', 'Register a new merchant account'
  def register(email, password)
    client = PayQI::Client.new

    begin
      merchant = client.register(email: email, password: password)
      say "? Successfully registered merchant: #{merchant['email']}", :green
      say "Merchant ID: #{merchant['id']}", :cyan
    rescue PayQI::APIError => e
      say "? Error: #{e.message}", :red
      exit 1
    end
  end

  desc 'login EMAIL PASSWORD', 'Login and get access token'
  def login(email, password)
    client = PayQI::Client.new

    begin
      result = client.login(email: email, password: password)
      token = result['access_token']

      say '? Login successful!', :green
      say "\nAccess Token:", :cyan
      say token, :yellow
      say "\n?? Save this token: export PAYQI_TOKEN='#{token}'", :cyan

      # Save to .env file
      unless File.readlines('.env').any? { |line| line.include?('PAYQI_TOKEN') }
        File.open('.env', 'a') { |f| f.puts "PAYQI_TOKEN=#{token}\n" }
      end

    rescue PayQI::APIError => e
      say "? Error: #{e.message}", :red
      exit 1
    end
  end

  desc 'payment AMOUNT CURRENCY', 'Create a new payment (requires PAYQI_TOKEN)'
  def payment(amount, currency)
    token = ENV['PAYQI_TOKEN']
    unless token
      say "? Error: PAYQI_TOKEN not found. Run 'payqi login' first.", :red
      exit 1
    end

    client = PayQI::Client.new
    currency = currency.upcase

    begin
      result = client.create_payment(
        amount: amount.to_f,
        currency: currency,
        access_token: token
      )

      say "\n? Payment created successfully!", :green
      say "\nPayment Details:", :cyan
      say "  Payment ID: #{result['payment_id']}", :yellow
      say "  Status: #{result['status']}", :yellow
      say "  Currency: #{currency}", :yellow
      say "  Amount: $#{amount}", :yellow

      if result['pay_address']
        say "\nPayment Address:", :cyan
        say "  #{result['pay_address']}", :yellow
      end

      if result['provider_invoice_id'] && currency == 'XRP'
        say "\n?? XRP Payment Instructions:", :cyan
        tag = result['provider_invoice_id'].split('_').last
        say "  Send XRP to the address above with destination tag: #{tag}", :yellow
      end
    rescue PayQI::APIError => e
      say "? Error: #{e.message}", :red
      exit 1
    end
  end

  desc 'status PAYMENT_ID', 'Get payment status'
  def status(payment_id)
    token = ENV['PAYQI_TOKEN']
    unless token
      say "? Error: PAYQI_TOKEN not found. Run 'payqi login' first.", :red
      exit 1
    end

    client = PayQI::Client.new

    begin
      result = client.get_payment(payment_id: payment_id, access_token: token)

      say "\nPayment Status:", :cyan
      say "  ID: #{result['id']}", :yellow
      say "  Status: #{result['status']}", :yellow
      say "  Amount: #{result['amount']} #{result['currency']}", :yellow
      say "  Created: #{result['created_at']}", :yellow

      say "  Transaction Hash: #{result['tx_hash']}", :yellow if result['tx_hash']
    rescue PayQI::APIError => e
      say "? Error: #{e.message}", :red
      exit 1
    end
  end

  desc 'transactions', 'List all transactions'
  def transactions
    token = ENV['PAYQI_TOKEN']
    unless token
      say "? Error: PAYQI_TOKEN not found. Run 'payqi login' first.", :red
      exit 1
    end

    client = PayQI::Client.new

    begin
      result = client.get_transactions(access_token: token)
      payments = result['items']

      if payments.empty?
        say 'No transactions found.', :yellow
        return
      end

      say "\n?? Transactions (#{payments.length}):", :cyan
      say "\n"

      payments.each do |payment|
        status_color = payment['status'] == 'completed' ? :green : :yellow
        status_text = payment['status'].upcase
        say "  #{payment['id']}. #{payment['amount']} #{payment['currency']} - #{status_text}", status_color
        say "     Created: #{payment['created_at']}", :white
      end
    rescue PayQI::APIError => e
      say "? Error: #{e.message}", :red
      exit 1
    end
  end

  desc 'merchant', 'Get current merchant info'
  def merchant
    token = ENV['PAYQI_TOKEN']
    unless token
      say "? Error: PAYQI_TOKEN not found. Run 'payqi login' first.", :red
      exit 1
    end

    client = PayQI::Client.new

    begin
      result = client.get_merchant(access_token: token)

      say "\n?? Merchant Information:", :cyan
      say "  ID: #{result['id']}", :yellow
      say "  Email: #{result['email']}", :yellow
      kyc_status = result['kyc_verified'] ? '?' : '?'
      kyc_color = result['kyc_verified'] ? :green : :yellow
      say "  KYC Verified: #{kyc_status}", kyc_color
      say "  Created: #{result['created_at']}", :yellow
    rescue PayQI::APIError => e
      say "? Error: #{e.message}", :red
      exit 1
    end
  end

  desc 'version', 'Show version'
  def version
    say 'PayQI CLI v1.0.0', :cyan
  end
end

PayQICLI.start(ARGV)
