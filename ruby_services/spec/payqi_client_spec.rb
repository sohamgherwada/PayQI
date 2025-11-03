# frozen_string_literal: true

require 'spec_helper'

RSpec.describe PayQI::Client do
  let(:api_url) { 'http://localhost:8000' }
  let(:client) { PayQI::Client.new(api_url: api_url) }

  describe '#initialize' do
    it 'creates a client with default URL' do
      client = PayQI::Client.new
      expect(client.api_url).to be_a(String)
    end

    it 'creates a client with custom URL' do
      expect(client.api_url).to eq(api_url)
    end
  end

  describe '#register' do
    it 'sends registration request' do
      connection_double = double('connection')
      allow(Faraday).to receive(:new).and_return(connection_double)
      response_double = double('response',
                               success?: true,
                               body: { id: 1, email: 'test@example.com' })
      allow(connection_double).to receive(:post).and_return(response_double)

      result = client.register(email: 'test@example.com', password: 'pass123')
      expect(result['email']).to eq('test@example.com')
    end
  end

  describe '#login' do
    it 'sends login request and returns token' do
      connection_double = double('connection')
      allow(Faraday).to receive(:new).and_return(connection_double)
      response_double = double('response',
                               success?: true,
                               body: { access_token: 'token123', token_type: 'bearer' })
      allow(connection_double).to receive(:post).and_return(response_double)

      result = client.login(email: 'test@example.com', password: 'pass123')
      expect(result['access_token']).to eq('token123')
    end

    it 'raises APIError on failure' do
      connection_double = double('connection')
      allow(Faraday).to receive(:new).and_return(connection_double)
      response_double = double('response',
                               success?: false,
                               status: 401,
                               body: { 'detail' => 'Invalid credentials' })
      allow(connection_double).to receive(:post).and_return(response_double)

      expect do
        client.login(email: 'test@example.com', password: 'wrong')
      end.to raise_error(PayQI::APIError)
    end
  end

  describe '#create_payment' do
    it 'sends payment creation request' do
      connection_double = double('connection')
      allow(Faraday).to receive(:new).and_return(connection_double)
      response_double = double('response',
                               success?: true,
                               body: { payment_id: 1, status: 'pending' })
      allow(connection_double).to receive(:post).and_return(response_double)

      result = client.create_payment(
        amount: 10.0,
        currency: 'XRP',
        access_token: 'token123'
      )
      expect(result['payment_id']).to eq(1)
    end
  end

  describe '#get_payment' do
    it 'fetches payment details' do
      connection_double = double('connection')
      allow(Faraday).to receive(:new).and_return(connection_double)
      response_double = double('response',
                               success?: true,
                               body: { id: 1, amount: 10.0, currency: 'XRP' })
      allow(connection_double).to receive(:get).and_return(response_double)

      result = client.get_payment(payment_id: 1, access_token: 'token123')
      expect(result['id']).to eq(1)
    end
  end

  describe '#get_transactions' do
    it 'fetches transactions list' do
      connection_double = double('connection')
      allow(Faraday).to receive(:new).and_return(connection_double)
      response_double = double('response',
                               success?: true,
                               body: { items: [{ id: 1 }, { id: 2 }] })
      allow(connection_double).to receive(:get).and_return(response_double)

      result = client.get_transactions(access_token: 'token123')
      expect(result['items'].length).to eq(2)
    end
  end

  describe 'APIError' do
    it 'has status_code attribute' do
      error = PayQI::APIError.new('Test error', 404)
      expect(error.status_code).to eq(404)
      expect(error.message).to eq('Test error')
    end
  end
end
