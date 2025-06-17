# Stripe Payment Flow Integration Guide

This guide provides the necessary steps to complete the Stripe payment flow integration with the VS Code extension frontend.

## Overview

The backend is already configured with Stripe API keys and has endpoints for subscription management. The frontend needs to implement the UI components to collect payment information securely and complete the payment flow.

## Prerequisites

1. Backend server running with the configured Stripe API keys
2. VS Code extension codebase
3. Access to Stripe Dashboard (for testing and monitoring)

## Implementation Steps

### 1. Install Required Dependencies

Add these dependencies to your VS Code extension:

```json
{
  "dependencies": {
    "@stripe/stripe-js": "^1.52.1",
    "axios": "^1.4.0"
  }
}
```

Install using:

```bash
npm install @stripe/stripe-js axios
```

### 2. Create a Payment Webview

Create a webview in your VS Code extension to display the payment form:

```typescript
// payment-webview.ts
import * as vscode from 'vscode';

export class PaymentWebviewPanel {
  public static currentPanel: PaymentWebviewPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  private constructor(panel: vscode.WebviewPanel, clientSecret: string, planName: string, price: string) {
    this._panel = panel;
    this._panel.webview.html = this._getWebviewContent(clientSecret, planName, price);
    
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    
    // Handle messages from the webview
    this._panel.webview.onDidReceiveMessage(
      message => {
        switch (message.command) {
          case 'paymentSuccess':
            vscode.window.showInformationMessage(`Successfully subscribed to ${planName}!`);
            this._panel.dispose();
            break;
          case 'paymentError':
            vscode.window.showErrorMessage(`Payment failed: ${message.error}`);
            break;
        }
      },
      null,
      this._disposables
    );
  }

  public static createOrShow(clientSecret: string, planName: string, price: string) {
    if (PaymentWebviewPanel.currentPanel) {
      PaymentWebviewPanel.currentPanel._panel.reveal();
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      'stripePayment',
      `Subscribe to ${planName}`,
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: []
      }
    );

    PaymentWebviewPanel.currentPanel = new PaymentWebviewPanel(panel, clientSecret, planName, price);
  }

  private _getWebviewContent(clientSecret: string, planName: string, price: string) {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Subscribe to ${planName}</title>
      <script src="https://js.stripe.com/v3/"></script>
      <style>
        body {
          font-family: Arial, sans-serif;
          line-height: 1.6;
          padding: 20px;
          color: var(--vscode-foreground);
          background-color: var(--vscode-editor-background);
        }
        .container {
          max-width: 500px;
          margin: 0 auto;
        }
        h1 {
          color: var(--vscode-editor-foreground);
        }
        .card-element {
          padding: 10px;
          border: 1px solid var(--vscode-input-border);
          border-radius: 4px;
          background: var(--vscode-input-background);
          margin-bottom: 20px;
        }
        button {
          padding: 10px 15px;
          background: var(--vscode-button-background);
          color: var(--vscode-button-foreground);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }
        button:hover {
          background: var(--vscode-button-hoverBackground);
        }
        .error {
          color: var(--vscode-errorForeground);
          margin-top: 10px;
        }
        .success {
          color: var(--vscode-notificationsInfoIcon-foreground);
          margin-top: 10px;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Subscribe to ${planName}</h1>
        <p>You are about to subscribe to the ${planName} for ${price} per month.</p>
        
        <form id="payment-form">
          <div id="card-element" class="card-element">
            <!-- Stripe Card Element will be inserted here -->
          </div>
          
          <div id="card-errors" class="error" role="alert"></div>
          
          <button id="submit-button" type="submit">Subscribe Now</button>
        </form>
        
        <div id="success-message" class="success" style="display:none;">
          Payment processed successfully! Your subscription is now active.
        </div>
      </div>

      <script>
        (function() {
          const stripe = Stripe('${process.env.STRIPE_PUBLISHABLE_KEY}');
          const clientSecret = '${clientSecret}';
          
          const elements = stripe.elements();
          const cardElement = elements.create('card');
          cardElement.mount('#card-element');

          const form = document.getElementById('payment-form');
          const errorElement = document.getElementById('card-errors');
          const successElement = document.getElementById('success-message');
          
          cardElement.on('change', function(event) {
            if (event.error) {
              errorElement.textContent = event.error.message;
            } else {
              errorElement.textContent = '';
            }
          });
          
          form.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            const submitButton = document.getElementById('submit-button');
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';
            
            try {
              const result = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                  card: cardElement,
                  billing_details: {
                    name: 'VS Code User'
                  }
                }
              });
              
              if (result.error) {
                // Show error to your customer
                errorElement.textContent = result.error.message;
                submitButton.disabled = false;
                submitButton.textContent = 'Subscribe Now';
                
                // Send error to extension
                const vscode = acquireVsCodeApi();
                vscode.postMessage({
                  command: 'paymentError',
                  error: result.error.message
                });
              } else {
                // Payment succeeded
                form.style.display = 'none';
                successElement.style.display = 'block';
                
                // Send success to extension
                const vscode = acquireVsCodeApi();
                vscode.postMessage({
                  command: 'paymentSuccess',
                  paymentIntent: result.paymentIntent
                });
              }
            } catch (e) {
              errorElement.textContent = e.message || 'An unexpected error occurred.';
              submitButton.disabled = false;
              submitButton.textContent = 'Subscribe Now';
            }
          });
        })();
      </script>
    </body>
    </html>`;
  }

  public dispose() {
    PaymentWebviewPanel.currentPanel = undefined;
    
    this._panel.dispose();

    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }
}
```

### 3. Create a Subscription Service

Create a service to handle subscription-related operations:

```typescript
// subscription-service.ts
import axios from 'axios';
import * as vscode from 'vscode';
import { PaymentWebviewPanel } from './payment-webview';

export class SubscriptionService {
  private baseUrl: string;
  private accessToken: string;

  constructor(baseUrl: string, accessToken: string) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
  }

  // Get all subscription plans
  async getSubscriptionPlans() {
    try {
      const response = await axios.get(`${this.baseUrl}/subscriptions/plans`, {
        headers: { Authorization: `Bearer ${this.accessToken}` }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching subscription plans:', error);
      throw error;
    }
  }

  // Get current subscription
  async getCurrentSubscription() {
    try {
      const response = await axios.get(`${this.baseUrl}/subscriptions/current`, {
        headers: { Authorization: `Bearer ${this.accessToken}` }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching current subscription:', error);
      throw error;
    }
  }

  // Subscribe to a plan
  async subscribeToPlan(planName: string) {
    try {
      // For free plan, direct subscription
      if (planName === 'free') {
        const response = await axios.post(`${this.baseUrl}/subscriptions/subscribe`,
          { plan_name: planName },
          { headers: { Authorization: `Bearer ${this.accessToken}` } }
        );
        vscode.window.showInformationMessage(`Successfully subscribed to ${planName} plan!`);
        return response.data;
      }
      
      // For paid plans, start Stripe flow
      const response = await axios.post(`${this.baseUrl}/subscriptions/subscribe`,
        { plan_name: planName },
        { headers: { Authorization: `Bearer ${this.accessToken}` } }
      );
      
      if (response.data.client_secret) {
        // Get plan details for display
        const plans = await this.getSubscriptionPlans();
        const plan = plans.find((p: any) => p.name === planName);
        const price = `$${plan.price_usd}`;
        
        // Show payment form
        PaymentWebviewPanel.createOrShow(
          response.data.client_secret,
          plan.display_name,
          price
        );
      }
      
      return response.data;
    } catch (error) {
      console.error('Error subscribing to plan:', error);
      vscode.window.showErrorMessage(`Failed to subscribe to ${planName} plan. Please try again.`);
      throw error;
    }
  }
}
```

### 4. Add Subscription Commands to Extension

Update your extension's activation function to add subscription commands:

```typescript
// extension.ts
import * as vscode from 'vscode';
import { SubscriptionService } from './subscription-service';
import { apiService } from './api-service'; // Your existing API service

export function activate(context: vscode.ExtensionContext) {
  // Get credentials from your auth service
  const { accessToken, baseUrl } = apiService.getCredentials();
  const subscriptionService = new SubscriptionService(baseUrl, accessToken);
  
  // Command to show subscription plans
  let plansCommand = vscode.commands.registerCommand('extension.showSubscriptionPlans', async () => {
    try {
      const plans = await subscriptionService.getSubscriptionPlans();
      
      // Format plans for quick pick
      const items = plans.map((plan: any) => ({
        label: plan.display_name,
        description: `$${plan.price_usd}/month`,
        detail: `${plan.monthly_tokens.toLocaleString()} tokens per month`,
        plan: plan.name
      }));
      
      const selected = await vscode.window.showQuickPick(items, {
        placeHolder: 'Select a subscription plan'
      });
      
      if (selected) {
        await subscriptionService.subscribeToPlan(selected.plan);
      }
    } catch (error) {
      vscode.window.showErrorMessage('Failed to retrieve subscription plans.');
    }
  });
  
  // Command to show current subscription
  let currentSubCommand = vscode.commands.registerCommand('extension.showCurrentSubscription', async () => {
    try {
      const subscription = await subscriptionService.getCurrentSubscription();
      
      if (subscription.has_subscription) {
        const plan = subscription.plan;
        vscode.window.showInformationMessage(
          `Current Plan: ${plan.display_name}\n` +
          `Monthly Tokens: ${plan.monthly_tokens.toLocaleString()}\n` +
          `Expires: ${new Date(subscription.expires_at).toLocaleDateString()}`
        );
      } else {
        vscode.window.showInformationMessage('You are on the free plan.');
      }
    } catch (error) {
      vscode.window.showErrorMessage('Failed to retrieve current subscription.');
    }
  });
  
  context.subscriptions.push(plansCommand, currentSubCommand);
}
```

### 5. Update package.json

Add the commands to your package.json file:

```json
"contributes": {
  "commands": [
    {
      "command": "extension.showSubscriptionPlans",
      "title": "Select Subscription Plan"
    },
    {
      "command": "extension.showCurrentSubscription",
      "title": "View Current Subscription"
    }
  ],
  "menus": {
    "commandPalette": [
      {
        "command": "extension.showSubscriptionPlans",
        "when": "editorIsOpen"
      },
      {
        "command": "extension.showCurrentSubscription",
        "when": "editorIsOpen"
      }
    ]
  }
}
```

## Testing the Integration

1. Start the backend server
2. Launch VS Code with your extension
3. Log in to your account
4. Use the "Select Subscription Plan" command
5. Choose a paid plan and complete the payment form
6. Verify the subscription is active using "View Current Subscription"

## Common Issues and Troubleshooting

1. **Payment form not showing**: Check that `enableScripts: true` is set in the webview options
2. **Stripe not defined**: Ensure the Stripe.js script is loaded before accessing it
3. **CORS issues**: Make sure the backend allows requests from your extension
4. **Authentication errors**: Verify the access token is valid and included in headers

## Webhook Implementation

For a complete solution, implement a webhook handler in the backend to process Stripe events:

1. Set up a webhook endpoint (e.g., `/webhooks/stripe`)
2. Configure this URL in the Stripe Dashboard
3. Verify webhook signatures using the webhook secret
4. Handle key events like `invoice.paid`, `subscription.created`, etc.

## Security Best Practices

1. **Never** store credit card information in your extension
2. Always use Stripe Elements for card collection
3. Use HTTPS for all API communications
4. Validate the webhook signature to prevent fake events
5. Handle errors gracefully and provide clear feedback to users

## Conclusion

Following these steps will allow you to integrate Stripe payments into your VS Code extension. The combination of the existing backend and this frontend implementation creates a complete subscription management system for your users.

Remember to test thoroughly in development mode before going live with real payments.
