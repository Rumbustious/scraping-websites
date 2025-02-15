"use client";
import React, { useState } from "react";
import axios from "axios";
import Link from "next/link";
import "./App.css";
import Skeleton from "./Skeleton";

export default function Home() {
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showMore, setShowMore] = useState({});

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/search?q=${encodeURIComponent(searchTerm)}`
      );
      setProducts(response.data.products);
    } catch (error) {
      console.error("Error fetching products:", error);
      setError("Failed to fetch products. Please try again.");
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
      <h1 className="text-4xl m-3">
        Start your product search over online stores.
      </h1>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Enter search term"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      {loading && (
        <div className="product-grid">
          {Array.from({ length: 10 }).map((_, index) => (
            <Skeleton key={index} />
          ))}
        </div>
      )}
      {error && <div className="error">{error}</div>}
      {!loading && (
        <div className="product-grid">
          {products.map((product, index) => (
            <div key={index} className="product-card">
              <img
                src={
                  product.store === "Jarir" ? "/jarir.svg" : "/Amazon_logo.svg"
                }
                alt={`${product.store} Logo`}
                className="store-logo"
              />
              <img src={product.image_url} alt={product.title} />
              <h3>{product.title}</h3>
              <p className="price">
                {product.price} <span className="currency">SAR</span>
              </p>
              <div className="rating">
                {product.rating} <span className="star-icon">★</span>
              </div>
              <div className="info">
                {product.info
                  .split(" | ")
                  .slice(0, showMore[index] ? undefined : 3)
                  .map((feature, idx) => (
                    <span key={idx} className="info-box">
                      {feature}
                    </span>
                  ))}
                {product.info.split(" | ").length > 3 && (
                  <button
                    className="show-more-button"
                    onClick={() => toggleShowMore(index)}
                  >
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
      )}
    </div>
  );
}