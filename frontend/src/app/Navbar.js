import React from "react";
import Link from "next/link";
import Image from "next/image";

const Navbar = () => {
  return (
    <nav className="bg-green-600 bg-opacity-75 p-4 flex justify-between items-center">
      <div className="flex items-center">
        <Image
          src="/logo.jpg"
          alt="Logo"
          width={100}
          height={40}
          className="mr-4"
        />
      </div>
      <div className="text-white text-xl font-bold justify-center">
        Store Scraper
      </div>
    </nav>
  );
};

export default Navbar;
