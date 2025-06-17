# VS Code Extension Integration Changes for Stripe Payment Flow

This document outlines the necessary files and changes needed to implement the Stripe payment flow in your VS Code extension.

## Files to Create/Modify

### 1. package.json

Add the required dependencies and commands:

```json
{
  "name": "autogen-code-builder",
  "displayName": "AutoGen Code Builder",
  "version": "1.0.0",
  "description": "VS Code extension for AutoGen Code Builder with A4F integration and subscription management",
  "engines": {
    "vscode": "^1.60.0"
  },
  "main": "./dist/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "autogen.showSubscriptionPlans",
        "title": "AutoGen: Select Subscription Plan"
      },
      {
        "command": "autogen.showCurrentSubscription",
        "title": "AutoGen: View Current Subscription"
      },
      {
        "command": "autogen.login",
        "title": "AutoGen: Login"
      },
      {
        "command": "autogen.logout",
        "title": "AutoGen: Logout"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "npm run package",
    "compile": "webpack",
    "watch": "webpack --watch",
    "package": "webpack --mode production --devtool hidden-source-map",
    "test-compile": "tsc -p ./",
    "test": "jest"
  },
  "dependencies": {
    "@stripe/stripe-js": "^1.52.1",
    "axios": "^1.4.0",
    "node-polyfill-webpack-plugin": "^2.0.1",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "@types/glob": "^8.1.0",
    "@types/node": "^18.15.11",
    "@types/vscode": "^1.60.0",
    "@types/jest": "^29.5.0",
    "jest": "^29.5.0",
    "ts-jest": "^29.1.0",
    "ts-loader": "^9.4.2",
    "typescript": "^5.0.4",
    "webpack": "^5.78.0",
    "webpack-cli": "^5.0.1"
  }
}
```

### 2. secureStorage.ts

Create a secure storage utility for storing tokens:

```typescript
import * as vscode from 'vscode';
import { v4 as uuid } from 'uuid';

export class SecureStorage {
    private context: vscode.ExtensionContext;
    private namespace: string;

    constructor(context: vscode.ExtensionContext, namespace: string = 'autogen') {
        this.context = context;
        this.namespace = namespace;
    }

    private getKey(key: string): string {
        return `${this.namespace}.${key}`;
    }

    async store(key: string, value: string): Promise<void> {
        await this.context.secrets.store(this.getKey(key), value);
    }

    async get(key: string): Promise<string | undefined> {
        return await this.context.secrets.get(this.getKey(key));
    }

    async delete(key: string): Promise<void> {
        await this.context.secrets.delete(this.getKey(key));
    }

    async has(key: string): Promise<boolean> {
        const value = await this.get(key);
        return value !== undefined;
    }

    async clear(): Promise<void> {
        const keys = ['accessToken', 'refreshToken', 'userId', 'email', 'a4fApiKey'];
        for (const key of keys) {
            await this.delete(key);
        }
    }

    // Token-specific methods
    async storeTokens(accessToken: string, refreshToken: string): Promise<void> {
        await this.store('accessToken', accessToken);
        await this.store('refreshToken', refreshToken);
    }

    async getTokens(): Promise<{ accessToken?: string, refreshToken?: string }> {
        const accessToken = await this.get('accessToken');
        const refreshToken = await this.get('refreshToken');
        return { accessToken, refreshToken };
    }

    async clearTokens(): Promise<void> {
        await this.delete('accessToken');
        await this.delete('refreshToken');
    }

    // A4F API Key storage
    async storeA4FApiKey(apiKey: string): Promise<void> {
        await this.store('a4fApiKey', apiKey);
    }

    async getA4FApiKey(): Promise<string | undefined> {
        return await this.get('a4fApiKey');
    }
}
```

### 3. backendService.ts

Create the backend service to handle API calls including subscription management:

```typescript
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import * as vscode from 'vscode';
import { SecureStorage } from './utils/secureStorage';

export class BackendService {
    private httpClient: AxiosInstance;
    private secureStorage: SecureStorage;
    private baseUrl: string;

    constructor(secureStorage: SecureStorage) {
        this.secureStorage = secureStorage;
        this.baseUrl = vscode.workspace.getConfiguration().get('autogen.apiEndpoint', 'http://localhost:8000');
        
        this.httpClient = axios.create({
            baseURL: this.baseUrl,
            timeout: 10000,
        });

        // Add request interceptor for authentication
        this.httpClient.interceptors.request.use(async config => {
            const { accessToken } = await this.secureStorage.getTokens();
            if (accessToken) {
                config.headers.Authorization = `Bearer ${accessToken}`;
            }
            return config;
        });

        // Add response interceptor for token refresh
        this.httpClient.interceptors.response.use(
            response => response,
            async error => {
                if (error.response?.status === 401) {
                    // Try to refresh token if unauthorized
                    const refreshed = await this.refreshToken();
                    if (refreshed) {
                        // Retry the original request
                        const { accessToken } = await this.secureStorage.getTokens();
                        error.config.headers.Authorization = `Bearer ${accessToken}`;
                        return this.httpClient.request(error.config);
                    }
                }
                return Promise.reject(error);
            }
        );
    }

    // Authentication methods
    async login(email: string, password: string): Promise<boolean> {
        try {
            const response = await this.httpClient.post('/auth/login-json', {
                email,
                password
            });

            if (response.data && response.data.access_token) {
                await this.secureStorage.storeTokens(
                    response.data.access_token,
                    response.data.refresh_token
                );

                // Store A4F API key if provided
                if (response.data.a4f_api_key) {
                    await this.secureStorage.storeA4FApiKey(response.data.a4f_api_key);
                }

                return true;
            }
            return false;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async refreshToken(): Promise<boolean> {
        try {
            const { refreshToken } = await this.secureStorage.getTokens();
            if (!refreshToken) {
                return false;
            }

            const response = await axios.post(`${this.baseUrl}/auth/refresh`, {
                refresh_token: refreshToken
            });

            if (response.data && response.data.access_token) {
                await this.secureStorage.storeTokens(
                    response.data.access_token,
                    response.data.refresh_token || refreshToken
                );
                return true;
            }
            return false;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    }

    async logout(): Promise<void> {
        await this.secureStorage.clearTokens();
    }

    // Get user profile
    async getUserProfile(): Promise<any> {
        try {
            const response = await this.httpClient.get('/users/me');
            return response.data;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            throw error;
        }
    }

    // Subscription methods
    async getSubscriptionPlans(): Promise<any[]> {
        try {
            const response = await this.httpClient.get('/subscriptions/plans');
            return response.data;
        } catch (error) {
            console.error('Error fetching subscription plans:', error);
            throw error;
        }
    }

    async getCurrentSubscription(): Promise<any> {
        try {
            const response = await this.httpClient.get('/subscriptions/current');
            return response.data;
        } catch (error) {
            console.error('Error fetching current subscription:', error);
            throw error;
        }
    }

    async subscribeToPlan(planName: string): Promise<any> {
        try {
            const response = await this.httpClient.post('/subscriptions/subscribe', {
                plan_name: planName
            });
            return response.data;
        } catch (error) {
            console.error('Error subscribing to plan:', error);
            throw error;
        }
    }

    // Usage statistics
    async getUsageStatistics(): Promise<any> {
        try {
            const response = await this.httpClient.get('/usage/stats');
            return response.data;
        } catch (error) {
            console.error('Error fetching usage statistics:', error);
            throw error;
        }
    }

    // VS Code configuration
    async getVSCodeConfig(): Promise<any> {
        try {
            const response = await this.httpClient.get('/vscode/config');
            return response.data;
        } catch (error) {
            console.error('Error fetching VS Code config:', error);
            throw error;
        }
    }

    // Available models
    async getAvailableModels(): Promise<any> {
        try {
            const response = await this.httpClient.get('/models/available');
            return response.data;
        } catch (error) {
            console.error('Error fetching available models:', error);
            throw error;
        }
    }

    // LLM request execution
    async executeLLMRequest(request: any): Promise<any> {
        try {
            const response = await this.httpClient.post('/llm/execute', request);
            return response.data;
        } catch (error) {
            console.error('Error executing LLM request:', error);
            throw error;
        }
    }
}
```

### 4. paymentWebview.ts

Create a class to handle the payment webview:

```typescript
import * as vscode from 'vscode';

export class PaymentWebviewPanel {
  public static currentPanel: PaymentWebviewPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  private constructor(panel: vscode.WebviewPanel, clientSecret: string, planName: string, price: string, stripePublishableKey: string) {
    this._panel = panel;
    this._panel.webview.html = this._getWebviewContent(clientSecret, planName, price, stripePublishableKey);
    
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

  public static createOrShow(clientSecret: string, planName: string, price: string, stripePublishableKey: string) {
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

    PaymentWebviewPanel.currentPanel = new PaymentWebviewPanel(panel, clientSecret, planName, price, stripePublishableKey);
  }

  private _getWebviewContent(clientSecret: string, planName: string, price: string, stripePublishableKey: string) {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Subscribe to ${planName}</title>
      <script src="https://js.stripe.com/v3/"></script>
      <style>
        body {
          font-family: var(--vscode-font-family);
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
          font-size: var(--vscode-font-size);
          font-weight: var(--vscode-font-weight);
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
          const stripe = Stripe('${stripePublishableKey}');
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

### 5. subscriptionService.ts

Create a service to handle subscription operations:

```typescript
import * as vscode from 'vscode';
import { BackendService } from './backendService';
import { PaymentWebviewPanel } from './paymentWebview';

export class SubscriptionService {
  private backendService: BackendService;
  private stripePublishableKey: string;

  constructor(backendService: BackendService) {
    this.backendService = backendService;
    this.stripePublishableKey = 'pk_test_51RVi9b00tZAh2watbNFlPjw4jKS02yZbKHQ1t97GcyMTOGLwcL8QhzxDSGtGuuEAJP4DHcEWOkut5N0CCTnuqBgh00p44dvGCb';
  }

  public async showSubscriptionPlans() {
    try {
      const plans = await this.backendService.getSubscriptionPlans();
      
      if (!plans || plans.length === 0) {
        vscode.window.showErrorMessage('No subscription plans found.');
        return;
      }

      // Format plans for quick pick
      const items = plans.map((plan: any) => ({
        label: plan.display_name || plan.name,
        description: `$${plan.price_monthly || plan.price_usd || 0}/month`,
        detail: `${plan.monthly_tokens ? plan.monthly_tokens.toLocaleString() : 'N/A'} tokens per month`,
        plan: plan.name
      }));
      
      const selected = await vscode.window.showQuickPick(items, {
        placeHolder: 'Select a subscription plan'
      });
      
      if (selected) {
        await this.subscribeToPlan(selected.plan);
      }
    } catch (error) {
      vscode.window.showErrorMessage('Failed to retrieve subscription plans: ' + this.getErrorMessage(error));
    }
  }

  public async showCurrentSubscription() {
    try {
      const subscription = await this.backendService.getCurrentSubscription();
      
      if (subscription.has_subscription) {
        const plan = subscription.plan;
        vscode.window.showInformationMessage(
          `Current Plan: ${plan.display_name || plan.name}\n` +
          `Monthly Tokens: ${plan.monthly_tokens ? plan.monthly_tokens.toLocaleString() : 'N/A'}\n` +
          `Expires: ${subscription.expires_at ? new Date(subscription.expires_at).toLocaleDateString() : 'N/A'}`
        );
      } else {
        vscode.window.showInformationMessage('You are currently on the free plan.');
      }
    } catch (error) {
      vscode.window.showErrorMessage('Failed to retrieve current subscription: ' + this.getErrorMessage(error));
    }
  }

  public async subscribeToPlan(planName: string) {
    try {
      vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Subscribing to ${planName} plan...`,
        cancellable: false
      }, async (progress) => {
        // For free plan, direct subscription
        if (planName === 'free') {
          const response = await this.backendService.subscribeToPlan(planName);
          vscode.window.showInformationMessage(`Successfully subscribed to ${planName} plan!`);
          return response;
        }
        
        // For paid plans, start Stripe flow
        const response = await this.backendService.subscribeToPlan(planName);
        
        if (response.client_secret) {
          // Get plan details for display
          const plans = await this.backendService.getSubscriptionPlans();
          const plan = plans.find((p: any) => p.name === planName);
          const price = `$${plan.price_monthly || plan.price_usd || 0}`;
          
          // Show payment form
          PaymentWebviewPanel.createOrShow(
            response.client_secret,
            plan.display_name || plan.name,
            price,
            this.stripePublishableKey
          );
        } else {
          vscode.window.showInformationMessage(response.message || `Subscription to ${planName} plan initiated.`);
        }
        
        return response;
      });
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to subscribe to ${planName} plan: ` + this.getErrorMessage(error));
    }
  }

  private getErrorMessage(error: any): string {
    if (error.response && error.response.data && error.response.data.detail) {
      return error.response.data.detail;
    }
    return error.message || 'Unknown error';
  }
}
```

### 6. extension.ts

Update the main extension file:

```typescript
import * as vscode from 'vscode';
import { SecureStorage } from './utils/secureStorage';
import { BackendService } from './backendService';
import { SubscriptionService } from './subscriptionService';

export function activate(context: vscode.ExtensionContext) {
  // Initialize services
  const secureStorage = new SecureStorage(context);
  const backendService = new BackendService(secureStorage);
  const subscriptionService = new SubscriptionService(backendService);

  // Register authentication commands
  const loginCommand = vscode.commands.registerCommand('autogen.login', async () => {
    const email = await vscode.window.showInputBox({
      prompt: 'Enter your email',
      placeHolder: 'user@example.com'
    });

    if (!email) {
      return;
    }

    const password = await vscode.window.showInputBox({
      prompt: 'Enter your password',
      password: true
    });

    if (!password) {
      return;
    }

    try {
      await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "Logging in...",
        cancellable: false
      }, async () => {
        const success = await backendService.login(email, password);
        if (success) {
          vscode.window.showInformationMessage('Successfully logged in!');
        } else {
          vscode.window.showErrorMessage('Login failed. Please check your credentials.');
        }
        return success;
      });
    } catch (error: any) {
      if (error.response && error.response.data && error.response.data.detail) {
        vscode.window.showErrorMessage(`Login failed: ${error.response.data.detail}`);
      } else {
        vscode.window.showErrorMessage(`Login failed: ${error.message || 'Unknown error'}`);
      }
    }
  });

  const logoutCommand = vscode.commands.registerCommand('autogen.logout', async () => {
    await secureStorage.clearTokens();
    vscode.window.showInformationMessage('Successfully logged out.');
  });

  // Register subscription commands
  const plansCommand = vscode.commands.registerCommand('autogen.showSubscriptionPlans', async () => {
    await subscriptionService.showSubscriptionPlans();
  });

  const currentSubCommand = vscode.commands.registerCommand('autogen.showCurrentSubscription', async () => {
    await subscriptionService.showCurrentSubscription();
  });

  // Register all commands to context
  context.subscriptions.push(
    loginCommand,
    logoutCommand,
    plansCommand,
    currentSubCommand
  );

  console.log('AutoGen extension has been activated.');
}

export function deactivate() {
  console.log('AutoGen extension has been deactivated.');
}
```

### 7. tsconfig.json

Create TypeScript configuration:

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "es2020",
    "outDir": "out",
    "lib": ["es2020", "DOM"],
    "sourceMap": true,
    "rootDir": ".",
    "strict": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedParameters": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
```

### 8. webpack.config.js

Create a webpack configuration file:

```javascript
//@ts-check

'use strict';

const path = require('path');
const NodePolyfillPlugin = require('node-polyfill-webpack-plugin');

/**@type {import('webpack').Configuration}*/
const config = {
  target: 'node',
  entry: './extension.ts',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'extension.js',
    libraryTarget: 'commonjs2',
    devtoolModuleFilenameTemplate: '../[resource-path]'
  },
  devtool: 'source-map',
  externals: {
    vscode: 'commonjs vscode'
  },
  resolve: {
    extensions: ['.ts', '.js']
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'ts-loader'
          }
        ]
      }
    ]
  },
  plugins: [
    new NodePolyfillPlugin()
  ]
};

module.exports = config;
```

## Implementation Steps

1. Create all the files listed above in the VS Code extension project
2. Run `npm install` to install all dependencies
3. Update the Stripe publishable key in `subscriptionService.ts` if needed
4. Test the extension by running:
   - `npm run compile` to compile
   - Press F5 in VS Code to launch the extension in debug mode

## Testing the Integration

1. Use the command "AutoGen: Login" to login to your account
2. Use the command "AutoGen: Select Subscription Plan" to view and select a plan
3. For paid plans, the Stripe payment form will appear
4. Use test card number 4242 4242 4242 4242, any future expiry date, and any CVC
5. After payment, use "AutoGen: View Current Subscription" to verify

## Key Features Implemented

1. ✅ Secure token storage using VS Code Secret Storage API
2. ✅ Backend service with authentication and subscription management
3. ✅ Stripe payment webview with secure card collection
4. ✅ Subscription plan selection and display
5. ✅ Error handling and user feedback
6. ✅ Token refresh support

## Additional Notes

- The Stripe publishable key is hardcoded in `subscriptionService.ts` - in a production environment, this should be fetched from the backend instead
- The payment form is styled to match VS Code's theme using CSS variables
- Error handling includes detailed messages from the backend when available

This implementation matches the backend services we've been testing, including the A4F API integration and subscription management.
