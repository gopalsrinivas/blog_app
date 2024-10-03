"use client";
import SeoMeta from "@layouts/partials/SeoMeta";
import { markdownify } from "@lib/utils/textConverter";
import axios from "axios";
import Link from "next/link";
import { useEffect, useState } from "react";

const Subcategories = ({ params }) => {
    const { subcategory } = params;
    const [subcategories, setSubcategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 12;

    // State for total records and total pages
    const [totalRecords, setTotalRecords] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [categoryName, setCategoryName] = useState("");
    const [error, setError] = useState(null);

    // Fetch subcategories based on subcategory ID and page
    const fetchSubcategories = async (page) => {
        try {
            const response = await axios.get(
                `${process.env.API_URL}/api/subcategories/categories/${subcategory}/subcategories?skip=${(page - 1) * itemsPerPage}&limit=${itemsPerPage}`
            );

            const { data, total_records, category_name } = response.data;

            setSubcategories(data);
            setTotalRecords(total_records);
            setCategoryName(category_name);
            setTotalPages(Math.ceil(total_records / itemsPerPage));
        } catch (error) {
            console.error("Error fetching subcategories:", error);
            setError("Failed to load subcategories. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (subcategory) {
            setLoading(true);
            fetchSubcategories(currentPage);
        }
    }, [subcategory, currentPage]);

    // Handle next page action
    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage((prevPage) => prevPage + 1);
        }
    };

    // Handle previous page action
    const handlePreviousPage = () => {
        if (currentPage > 1) {
            setCurrentPage((prevPage) => prevPage - 1);
        }
    };

    return (
        <>
            <SeoMeta title="Subcategories" />
            <section className="section min-h-dvh">
                <div className="container text-center">
                    {categoryName ? (
                        markdownify(`categories ==> (${categoryName})`, "h1", "h2 mb-3")
                    ) : (
                        <p>Loading category name...</p>
                    )}
                    <hr />

                    {markdownify(`Subcategories (${totalRecords})`, "h1", "h2 mt-10 mb-10")}
                    {loading ? (
                        <p>Loading subcategories...</p>
                    ) : error ? (
                        <p>{error}</p>
                    ) : subcategories.length > 0 ? (
                        <>
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-10">
                                {subcategories.map((subcategory) => (
                                    <div key={subcategory.id} className="inline-block">
                                        <Link
                                            href={`/blog/bloglist/${subcategory.id}`}
                                            className="rounded-lg bg-theme-light px-4 py-2 text-dark transition hover:bg-primary hover:text-white"
                                        >
                                            {subcategory.name}
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
                        <p>No subcategories found.</p>
                    )}
                </div>
            </section>
        </>
    );
};

export default Subcategories;
