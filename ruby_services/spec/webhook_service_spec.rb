# frozen_string_literal: true

require 'spec_helper'
require 'openssl'

RSpec.describe WebhookService do
  describe 'GET /health' do
    it 'returns ok status' do
      get '/health'
      expect(last_response.status).to eq(200)
      data = JSON.parse(last_response.body)
      expect(data['status']).to eq('ok')
      expect(data['service']).to eq('webhook-processor')
    end
  end

  describe 'POST /webhooks/nowpayments' do
    let(:secret) { 'test_secret_key' }
    let(:payload) { { payment_id: '123', status: 'confirmed' }.to_json }
    let(:signature) do
      OpenSSL::HMAC.hexdigest(
        OpenSSL::Digest.new('sha512'),
        secret,
        payload
      )
    end

    before do
      allow(ENV).to receive(:fetch).and_call_original
      allow(ENV).to receive(:fetch).with('NOWPAYMENTS_IPN_SECRET', nil).and_return(secret)
      allow(ENV).to receive(:fetch).with('PYTHON_API_URL', anything).and_return('http://localhost:8000')
    end

    context 'with valid signature' do
      it 'processes the webhook' do
        # Mock the Faraday connection
        connection_double = double('connection')
        allow(Faraday).to receive(:new).and_return(connection_double)
        response_double = double('response', success?: true, status: 200)
        allow(connection_double).to receive(:post).and_return(response_double)

        post '/webhooks/nowpayments', payload,
             { 'CONTENT_TYPE' => 'application/json',
               'HTTP_X_NOWPAYMENTS_SIG' => signature }

        expect(last_response.status).to eq(200)
        data = JSON.parse(last_response.body)
        expect(data['status']).to eq('ok')
      end
    end

    context 'with invalid signature' do
      it 'returns 401' do
        post '/webhooks/nowpayments', payload,
             { 'CONTENT_TYPE' => 'application/json',
               'HTTP_X_NOWPAYMENTS_SIG' => 'invalid_signature' }

        expect(last_response.status).to eq(401)
        data = JSON.parse(last_response.body)
        expect(data['error']).to eq('Invalid signature')
      end
    end

    context 'with missing signature' do
      it 'returns 401' do
        post '/webhooks/nowpayments', payload,
             { 'CONTENT_TYPE' => 'application/json' }

        expect(last_response.status).to eq(401)
      end
    end

    context 'with invalid JSON' do
      it 'returns 400' do
        post '/webhooks/nowpayments', 'invalid json',
             { 'CONTENT_TYPE' => 'application/json' }

        expect(last_response.status).to eq(400)
        data = JSON.parse(last_response.body)
        expect(data['error']).to eq('Invalid JSON')
      end
    end
  end

  describe 'POST /webhooks/xrp' do
    let(:valid_data) do
      {
        tx_hash: 'ABC123',
        destination_tag: '123456',
        amount: '50.0',
        currency: 'XRP'
      }.to_json
    end

    before do
      allow(ENV).to receive(:fetch).and_call_original
      allow(ENV).to receive(:fetch).with('PYTHON_API_URL', anything).and_return('http://localhost:8000')
    end

    context 'with valid XRP transaction data' do
      it 'processes the webhook' do
        connection_double = double('connection')
        allow(Faraday).to receive(:new).and_return(connection_double)
        response_double = double('response', success?: true, status: 200)
        allow(connection_double).to receive(:post).and_return(response_double)

        post '/webhooks/xrp', valid_data,
             { 'CONTENT_TYPE' => 'application/json' }

        expect(last_response.status).to eq(200)
        data = JSON.parse(last_response.body)
        expect(data['status']).to eq('ok')
      end
    end

    context 'with invalid XRP transaction data' do
      it 'returns 400 for missing fields' do
        invalid_data = { tx_hash: 'ABC123' }.to_json

        post '/webhooks/xrp', invalid_data,
             { 'CONTENT_TYPE' => 'application/json' }

        expect(last_response.status).to eq(400)
        data = JSON.parse(last_response.body)
        expect(data['error']).to eq('Invalid transaction data')
      end

      it 'returns 400 for wrong currency' do
        invalid_data = {
          tx_hash: 'ABC123',
          destination_tag: '123456',
          amount: '50.0',
          currency: 'BTC'
        }.to_json

        post '/webhooks/xrp', invalid_data,
             { 'CONTENT_TYPE' => 'application/json' }

        expect(last_response.status).to eq(400)
      end
    end
  end
end
