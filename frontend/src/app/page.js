"use client";
import React, { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import "./App.css";
import Skeleton from "./Skeleton";
import { FaStar, FaFilter } from "react-icons/fa";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";
import Navbar from "./Navbar"; // Import the Navbar component

async function processStream(reader, setProducts, setError) {
  /*...*/
}

const Sidebar = ({
  storeFilter,
  setStoreFilter,
  minPrice,
  setMinPrice,
  maxPrice,
  setMaxPrice,
  minRating,
  setMinRating,
  maxProductPrice,
  isOpen,
  toggleSidebar,
  resetFilters,
}) => {
  const handleStoreChange = (e) => {
    setStoreFilter(e.target.value);
  };

  const handleRatingChange = (rating) => {
    setMinRating((prevRating) => (prevRating === rating ? "" : rating));
  };

  return (
    <div
      className={`fixed top-0 left-0 h-full bg-gray-100 shadow-lg transform ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      } transition-transform duration-300 ease-in-out z-50`}
    >
      <div className="w-64 p-4">
        <button
          className="absolute top-4 right-4 text-gray-600"
          onClick={toggleSidebar}
        >
          ✕
        </button>
        <h2 className="text-xl font-bold mb-4 text-center">Filters</h2>
        <div className="mb-4">
          <label className="block mb-2 font-semibold text-center">Store</label>
          <select
            value={storeFilter}
            onChange={handleStoreChange}
            className="p-2 border border-gray-300 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Stores</option>
            <option value="Jarir">Jarir</option>
            <option value="Amazon">Amazon</option>
            <option value="Extra">Extra</option>
            <option value="Carrefour">Carrefour</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="block mb-2 font-semibold text-center">
            Price Range
          </label>
          <Slider
            range
            min={0}
            max={maxProductPrice}
            defaultValue={[minPrice, maxPrice]}
            onChange={([min, max]) => {
              setMinPrice(min);
              setMaxPrice(max);
            }}
          />
          <div className="flex justify-between mt-2">
            <span>{minPrice} SAR</span>
            <span>{maxPrice} SAR</span>
          </div>
        </div>
        <div className="mb-4">
          <label className="block mb-2 font-semibold text-center">Rating</label>
          <div className="flex justify-center">
            {[5, 4, 3, 2, 1, "All"].map((star) => (
              <button
                key={star}
                onClick={() => handleRatingChange(star)}
                className={`text-xl ${
                  minRating === star ? "text-yellow-500" : "text-gray-400"
                }`}
              >
                {star === "All" ? "All" : <FaStar />}
              </button>
            ))}
          </div>
        </div>
        <button
          className="w-full p-2 bg-red-500 text-white rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
          onClick={resetFilters}
        >
          Reset Filters
        </button>
      </div>
    </div>
  );
};

export default function Home() {
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showMore, setShowMore] = useState({});
  const [storeFilter, setStoreFilter] = useState("");
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(1000);
  const [minRating, setMinRating] = useState("");
  const [maxProductPrice, setMaxProductPrice] = useState(1000);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showHero, setShowHero] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    if (products.length > 0) {
      const maxPrice = Math.max(
        ...products.map((product) => parseFloat(product.price))
      );
      setMaxProductPrice(maxPrice);
      setMaxPrice(maxPrice);
    }
  }, [products]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prevSlide) => (prevSlide + 1) % 3);
    }, 3000); // Change slide every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    setLoading(true);
    setError(null);
    setProducts([]); // Clear previous results
    setShowHero(false); // Hide hero section

    try {
      const response = await fetch(
        `http://localhost:8000/api/search?q=${encodeURIComponent(searchTerm)}`
      );

      if (!response.ok) throw new Error("Failed to fetch");
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      await processStream(reader, setProducts, setError);
    } catch (error) {
      console.error("Error fetching products:", error);
      setError(error.message || "Failed to fetch products. Please try again.");
    }
    setLoading(false);
  };

  const toggleShowMore = (index) => {
    setShowMore((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const resetFilters = () => {
    setStoreFilter("");
    setMinPrice(0);
    setMaxPrice(maxProductPrice);
    setMinRating("");
  };

  const filteredProducts = products.filter((product) => {
    const price = parseFloat(product.price);
    const rating = parseFloat(product.rating);
    const matchesStore = storeFilter ? product.store === storeFilter : true;
    const matchesPrice =
      (!minPrice || price >= parseFloat(minPrice)) &&
      (!maxPrice || price <= parseFloat(maxPrice));
    const matchesRating =
      minRating === "All"
        ? true
        : !minRating || rating >= parseFloat(minRating);
    return matchesStore && matchesPrice && matchesRating;
  });

  return (
    <div className="relative pb-16">
      <Navbar />
      <div className="flex">
        <Sidebar
          storeFilter={storeFilter}
          setStoreFilter={setStoreFilter}
          minPrice={minPrice}
          setMinPrice={setMinPrice}
          maxPrice={maxPrice}
          setMaxPrice={setMaxPrice}
          minRating={minRating}
          setMinRating={setMinRating}
          maxProductPrice={maxProductPrice}
          isOpen={isSidebarOpen}
          toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          resetFilters={resetFilters}
        />
        <div className="container mx-auto p-4">
          <h1 className="text-4xl font-bold mb-6 text-center">
            Start your product search over online stores.
          </h1>
          <div className="search-bar flex justify-center mb-6">
            <input
              type="text"
              placeholder="Enter search term"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSearch}
              className="p-2 bg-blue-500 text-white rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Search
            </button>
            <button
              className="p-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 ml-2"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <FaFilter />
            </button>
          </div>
          {showHero && (
            <div className="hero-section relative">
              <div className="slides">
                <div
                  className={`slide ${
                    currentSlide === 0 ? "block" : "hidden"
                  } text-center`}
                >
                  <h2 className="text-4xl font-bold">Team Member</h2>
                  <p className="text-4xl">Abdullah Faleh Alotaibi</p>
                </div>
                <div
                  className={`slide ${
                    currentSlide === 1 ? "block" : "hidden"
                  } text-center`}
                >
                  <h2 className="text-4xl font-bold">Team Member</h2>
                  <p className="text-4xl">Saad Thaar Alqahtani</p>
                </div>
                <div
                  className={`slide ${
                    currentSlide === 2 ? "block" : "hidden"
                  } text-center`}
                >
                  <img
                    src="/logo.jpg"
                    alt="Logo"
                    className="mx-auto"
                    width={600}
                    height={40}
                  />
                </div>
              </div>
             
            </div>
          )}
          {loading && (
            <div className="product-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 10 }).map((_, index) => (
                <Skeleton key={index} />
              ))}
            </div>
          )}
          {error && (
            <div className="error text-red-500 text-center">{error}</div>
          )}
          {!loading && (
            <div className="product-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredProducts.map((product, index) => (
                <div
                  key={index}
                  className="product-card border p-4 rounded-md shadow-md"
                >
                  <img
                    src={
                      product.store === "Jarir"
                        ? "/jarir.svg"
                        : product.store === "Amazon"
                        ? "/Amazon_logo.svg"
                        : product.store === "Extra"
                        ? "/extra-logo.svg"
                        : "/carrefour.png"
                    }
                    alt={`${product.store} Logo`}
                    className="store-logo w-12 h-12 mb-4"
                  />
                  <img
                    src={product.image_url}
                    alt={product.title}
                    className="mb-4 mx-auto"
                  />
                  <h3 className="text-lg font-semibold mb-2">
                    {product.title}
                  </h3>
                  <p className="price text-red-500 font-bold mb-2">
                    {product.price} <span className="currency">SAR</span>
                  </p>
                  <div className="rating flex items-center mb-2">
                    {product.rating}{" "}
                    <span className="star-icon text-yellow-500 ml-1">★</span>
                  </div>
                  <div className="info mb-4">
                    {product.info
                      .split(" | ")
                      .slice(0, showMore[index] ? undefined : 3)
                      .map((feature, idx) => (
                        <span
                          key={idx}
                          className="info-box bg-gray-100 p-2 rounded-md mr-2 mb-2 inline-block"
                        >
                          {feature}
                        </span>
                      ))}
                    {product.info.split(" | ").length > 3 && (
                      <button
                        className="show-more-button text-blue-500 hover:underline"
                        onClick={() => toggleShowMore(index)}
                      >
                        {showMore[index] ? "Show Less" : "Show More"}
                      </button>
                    )}
                  </div>
                  <Link href={product.link} passHref>
                    <button className="view-product-button bg-green-500 text-white p-2 rounded-md hover:bg-green-600">
                      View Product
                    </button>
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}