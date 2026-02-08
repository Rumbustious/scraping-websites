import React from "react";
import Link from "next/link";
import Image from "next/image";

const Navbar = () => {
  return (
    <nav className="bg-green-600 bg-opacity-75 p-4 flex justify-between items-center">
      <div className="text-white text-xl font-bold justify-center">
        Store Scraper
      </div>
    </nav>
  );
};

export default Navbar;
