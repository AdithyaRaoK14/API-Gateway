from fastapi import FastAPI
app = FastAPI()

products = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Mouse", "price": 29.99},
    {"id": 3, "name": "Keyboard", "price": 79.99},
]

@app.get("/health")
def health():
    return {"status": "ok", "service": "product-service"}

@app.get("/products/")
def list_products():
    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):
    p = next((p for p in products if p["id"] == product_id), None)
    if not p:
        from fastapi import HTTPException
        raise HTTPException(404, "Not found")
    return p
