'use client'
import React, { useState } from "react";
import axios from "axios";
import Link from 'next/link';
import "./App.css";

export default function Home() {
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showMore, setShowMore] = useState({});

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

  const toggleShowMore = (index) => {
    setShowMore((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
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
            <img src="/jarir.svg" alt="Jarir Logo" className="jarir-logo" />
            <img src={product.image_url} alt={product.title} />
            <h3>{product.title}</h3>
            <p className="text-red-500 text-lg font-bold">{product.price} <span className="text-gray-600">SAR</span></p>
            <div className="rating">
              {product.rating} <span className="star-icon">★</span>
            </div>
            <div className="info">
              {product.info.split(" | ").slice(0, showMore[index] ? undefined : 3).map((feature, idx) => (
                <span key={idx} className="info-box">{feature}</span>
              ))}
              {product.info.split(" | ").length > 3 && (
                <button className="show-more-button" onClick={() => toggleShowMore(index)}>
                  {showMore[index] ? "Show Less" : "Show More"}
                </button>
              )}
            </div>
            <Link href={product.link} passHref>
              <button className="view-product-button">View Product</button>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}