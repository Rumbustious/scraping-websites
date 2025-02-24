import React from "react";
import Navbar from "@/app/Navbar.js";
import Image from "next/image";

const Team = () => {
  return (
    <div>
      <Navbar />
      <div className="container mx-auto p-4">
        <h1 className="text-4xl font-bold mb-6 text-center">Team Members</h1>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="col-span-1"></div> {/* Empty column */}
          <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center col-span-1">
            <Image
              src="/abdullah.jpg"
              alt="Abdullah Faleh Alotaibi"
              width={150}
              height={150}
              className="rounded mb-4"
            />
            <h2 className="text-xl font-semibold">Abdullah Faleh Alotaibi</h2>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center col-span-1">
            <Image
              src="/saad.jpg"
              alt="Saad Thaar Alqahtani"
              width={150}
              height={150}
              className="rounded mb-4"
            />
            <h2 className="text-xl font-semibold">Saad Thaar Alqahtani</h2>
          </div>
          <div className="col-span-1"></div> {/* Empty column */}
        </div>
      </div>
    </div>
  );
};

export default Team;