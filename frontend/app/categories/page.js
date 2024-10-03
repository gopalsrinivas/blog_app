"use client";
import SeoMeta from "@layouts/partials/SeoMeta";
import { markdownify } from "@lib/utils/textConverter";
import axios from "axios";
import Link from "next/link";
import { useEffect, useState } from "react";

const Categories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  // Total records and total pages state
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [error, setError] = useState(null);

  // Fetch categories and total records using Axios
  const fetchCategories = async (page) => {
    try {
      const response = await axios.get(
        `${process.env.API_URL}/api/categories/all/?skip=${(page - 1) * itemsPerPage}&limit=${itemsPerPage}`
      );
      setCategories(response.data.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
      setError("Failed to load categories. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const fetchTotalRecords = async () => {
    try {
      const response = await axios.get(`${process.env.API_URL}/api/categories/all/`);
      setTotalRecords(response.data.total_count);
      setTotalPages(Math.ceil(response.data.total_count / itemsPerPage));
    } catch (error) {
      console.error("Error fetching total records:", error);
      setError("Failed to load total record count. Please try again later.");
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      await fetchCategories(currentPage);
      await fetchTotalRecords();
    };

    fetchData();
  }, [currentPage]);

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage((prevPage) => prevPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage((prevPage) => prevPage - 1);
    }
  };

  return (
    <>
      <SeoMeta title="Categories" />
      <section className="section min-h-dvh">
        <div className="container text-center">
          {markdownify(`Categories (${totalRecords})`, "h1", "h2 mb-16")}
          {loading ? (
            <p>Loading categories...</p>
          ) : error ? (
            <p>{error}</p>
          ) : categories.length > 0 ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-10">
                {categories.map((category) => (
                  <div key={category.id} className="inline-block">
                    <Link
                      href={`/subcategories/${category.id}`}
                      className="rounded-lg bg-theme-light px-4 py-2 text-dark transition hover:bg-primary hover:text-white"
                    >
                      {category.name}
                    </Link>
                  </div>
                ))}
              </div>

              <nav className="flex justify-center space-x-4 pt-3.5" aria-label="Pagination">
                <button
                  onClick={handlePreviousPage}
                  disabled={currentPage === 1}
                  className={`rounded-lg border border-primary px-2 py-2 text-dark ${currentPage === 1 ? "bg-gray-300 cursor-not-allowed" : "bg-white hover:bg-primary hover:text-white"
                    }`}
                >
                  <span className="sr-only">Previous</span>
                  <svg
                    className="mt-1 h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
                <span className="rounded-lg border border-primary bg-primary px-4 py-2 text-white">
                  {currentPage}
                </span>
                <button
                  onClick={handleNextPage}
                  disabled={currentPage >= totalPages}
                  className={`rounded-lg border border-primary px-2 py-2 text-dark ${currentPage >= totalPages ? "bg-gray-300 cursor-not-allowed" : "bg-white hover:bg-primary hover:text-white"
                    }`}
                >
                  <span className="sr-only">Next</span>
                  <svg
                    className="mt-1 h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10l-3.293-3.293a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </nav>
            </>
          ) : (
            <p>No categories found.</p>
          )}
        </div>
      </section>
    </>
  );
};

export default Categories;
