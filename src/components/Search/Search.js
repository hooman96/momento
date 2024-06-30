import { useState } from "react"




const Search = ({onSearch})  => {

const[query,setQuery] = useState('')

const handleInputChange = (e) => {
    setQuery(e.target.value);
}

const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query);
}
   

    return (


        <>
        
         <div className=" flex items-center justify-center py-4 " >

          <form onSubmit={handleSearch}  className="relative w-64" >
            <input
            
            type="text"
            onChange={handleInputChange}
            value={query}
            placeholder="Search..."
            className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 "
            
            />
            <button
             type="submit"

             className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
            >
                <svg
                 className="w-4 h-4"
                 fill="none"
                 stroke="currentColor"
                 viewBox="0 0 24 24"
                 xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                     strokeLinecap="round"
                     strokeLinejoin="round"
                     strokeWidth="2"
                     d="M21 21l-4.35-4.35M16 10a6 6 0 11-12 0 6 6 0 0112 0z"
                    ></path>
                </svg>
            </button>
          </form>

         </div>


        </>
    )



}

export default Search