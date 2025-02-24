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
      <span className="text-white text-xl font-bold justify-center">
        Store Scraper
      </span>
      <div className="flex space-x-4">
        <Link
          href="/"
          className="text-white hover:bg-green-700 hover:text-gray-300 px-3 py-2 rounded-md"
        >
          Home
        </Link>
        <Link
          href="/team"
          className="text-white hover:bg-green-700 hover:text-gray-300 px-3 py-2 rounded-md"
        >
          Team Members
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
