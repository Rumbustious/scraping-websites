'use client'
import React, { useState } from "react";
import axios from "axios";
import "./App.css";

export default function Home() {
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/search?q=${encodeURIComponent(searchTerm)}`
      );
      setProducts(response.data.products);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1 className="text-4xl m-3">Start your product search over online stores.</h1>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Enter search term"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      {loading && <div className="loader">Loading...</div>}
      <div className="product-grid">
        {products.map((product, index) => (
          <div key={index} className="product-card">
            <img src={product.image_url} alt={product.title} />
            <h3>{product.title}</h3>
            <p>{product.price} SAR</p>
            <a href={product.link} target="_blank" rel="noopener noreferrer">
              View Product
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}