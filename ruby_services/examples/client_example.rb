#!/usr/bin/env ruby
# frozen_string_literal: true

# Example usage of PayQI Ruby client
# Demonstrates Ruby skills for Shopify applications

require_relative '../lib/payqi_client'
require 'dotenv'

Dotenv.load

# Initialize client
api_url = ENV.fetch('PAYQI_API_URL', 'http://localhost:8000')
client = PayQI::Client.new(api_url: api_url)

puts "?? PayQI Ruby Client Example"
puts "=" * 50

begin
  # Example: Register a new merchant
  puts "\n1. Registering merchant..."
  merchant = client.register(
    email: 'shop@example.com',
    password: 'securepassword123'
  )
  puts "? Registered: #{merchant['email']} (ID: #{merchant['id']})"

  # Example: Login
  puts "\n2. Logging in..."
  login_result = client.login(
    email: 'shop@example.com',
    password: 'securepassword123'
  )
  token = login_result['access_token']
  puts "? Logged in! Token: #{token[0..20]}..."

  # Example: Create XRP payment
  puts "\n3. Creating XRP payment..."
  payment = client.create_payment(
    amount: 25.50,
    currency: 'XRP',
    access_token: token
  )
  puts "? Payment created!"
  puts "   Payment ID: #{payment['payment_id']}"
  puts "   Status: #{payment['status']}"
  puts "   Address: #{payment['pay_address']}"
  
  if payment['provider_invoice_id']
    tag = payment['provider_invoice_id'].split('_').last
    puts "   Destination Tag: #{tag}"
  end

  # Example: Get payment status
  puts "\n4. Getting payment status..."
  payment_details = client.get_payment(
    payment_id: payment['payment_id'],
    access_token: token
  )
  puts "? Payment details:"
  puts "   Amount: #{payment_details['amount']} #{payment_details['currency']}"
  puts "   Status: #{payment_details['status']}"

  # Example: List transactions
  puts "\n5. Listing transactions..."
  transactions = client.get_transactions(access_token: token)
  puts "? Found #{transactions['items'].length} transactions"
  transactions['items'].each do |tx|
    puts "   - #{tx['amount']} #{tx['currency']} (#{tx['status']})"
  end

  # Example: Get merchant info
  puts "\n6. Getting merchant info..."
  merchant_info = client.get_merchant(access_token: token)
  puts "? Merchant Info:"
  puts "   Email: #{merchant_info['email']}"
  puts "   KYC Verified: #{merchant_info['kyc_verified'] ? 'Yes' : 'No'}"

rescue PayQI::APIError => e
  puts "? API Error (#{e.status_code}): #{e.message}"
rescue StandardError => e
  puts "? Error: #{e.message}"
  puts e.backtrace.first(3)
end

puts "\n" + "=" * 50
puts "? Example complete!"
