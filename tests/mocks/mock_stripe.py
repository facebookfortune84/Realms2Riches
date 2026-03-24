# tests/mocks/mock_stripe.py
import stripe

class MockStripeProduct:
    def __init__(self, id, name, description, metadata):
        self.id = id
        self.name = name
        self.description = description
        self.metadata = metadata

class MockStripePrice:
    def __init__(self, id, product, unit_amount, currency, recurring):
        self.id = id
        self.product = product
        self.unit_amount = unit_amount
        self.currency = currency
        self.recurring = recurring

class MockStripePaymentLink:
    def __init__(self, url):
        self.url = url

class MockStripe:
    products = []
    prices = []
    payment_links = []

    def __init__(self):
        self.Product = self
        self.Price = self
        self.PaymentLink = self
        self.api_key = None # To simulate settings.STRIPE_API_KEY
    
    def list(self, active=True, limit=100):
        return [p for p in self.products if active]

    def create(self, **kwargs):
        if 'name' in kwargs and 'description' in kwargs: # Product
            new_product = MockStripeProduct(
                id=f"prod_{len(self.products) + 1}",
                name=kwargs['name'],
                description=kwargs['description'],
                metadata=kwargs.get('metadata', {})
            )
            self.products.append(new_product)
            return new_product
        elif 'product' in kwargs and 'unit_amount' in kwargs: # Price
            new_price = MockStripePrice(
                id=f"price_{len(self.prices) + 1}",
                product=kwargs['product'],
                unit_amount=kwargs['unit_amount'],
                currency=kwargs['currency'],
                recurring=kwargs.get('recurring')
            )
            self.prices.append(new_price)
            return new_price
        elif 'line_items' in kwargs: # PaymentLink
            new_link = MockStripePaymentLink(url=f"https://buy.stripe.com/test_link_{len(self.payment_links) + 1}")
            self.payment_links.append(new_link)
            return new_link
        
        raise ValueError("Unknown Stripe object creation")

# Instantiate once for mocking
mock_stripe_client = MockStripe()
