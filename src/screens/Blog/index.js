import React from 'react';
import Search from '../../components/Search/Search';


const blogs = [

 {
      id:1,
      head:'From Mocha to Vitest ',
      status:'Articles',
      author:{
        name:'Vivek',
        image: 'https://via.placeholder.com/50',
      },
      date:'May 27, 2024'  
 },
 {
  id:2,
  head:'From Mocha to Vitest ',
  status:'Articles',
  author:{
    name:'Vivek',
    image: 'https://via.placeholder.com/50',
  },
  date:'May 27, 2024'  
},
{
  id:3,
  head:'From Mocha to Vitest ',
  status:'Articles',
  author:{
    name:'Vivek',
    image: 'https://via.placeholder.com/50',
  },
  date:'May 27, 2024'  
},
{
  id:4,
  head:'From Mocha to Vitest ',
  status:'Articles',
  author:{
    name:'Vivek',
    image: 'https://via.placeholder.com/50',
  },
  date:'May 27, 2024'  
},



]


const posts = [
  {
    id: 1,
    title: 'React and CodeMod Announcement',
    summary: 'We are excited to announce that we are partnering with the React Team.',
    image: 'https://cdn.sanity.io/images/aho0e32c/production/7556fba6f2d7435a3d26d05678c62ca3cb6174c2-1024x496.png?w=850&fit=max&auto=format',
    author: {
      name: 'Vivek',
      image: 'https://via.placeholder.com/50',
    },
    date: 'May 7, 2024'
  },
  {
    id: 2,
    title: 'CodeMod AI',
    summary: 'We are excited to announce that we are partnering with the React Team.',
    image: 'https://cdn.sanity.io/images/aho0e32c/production/3a2788edb7ed7bdd5331f445856cfe5a8db1486b-1012x506.svg?w=850&fit=max&auto=format',
    author: {
      name: 'Vivek',
      image: 'https://via.placeholder.com/50',
    },
    date: 'May 7, 2024'
  },
  // Add more posts here
];

const Blog = () => {

  const handleSearch = (query) =>{
    console.log('Searching for : ', query)
  }

  return (

    <> 
     
    <div className="container mx-auto px-4 py-8">
    <div className='grid grid-cols-2 mb-8 ' >
      <div className='grid grid-cols-5 ' > 
        <div className='container mx-auto px-2 py-4 justify-center ' >
        <div className="w-30 h-18 bg-gray-200 hover:bg-blue-500 transform hover:scale-105 transition duration-300 ease-in-out flex items-center justify-center  font-semibold   text-gray-800 hover:text-white rounded-lg shadow-md hover:shadow-lg">
        All Posts
      </div>
        </div>
        <div className='container mx-auto px-2 py-4 justify-center ' >
        <div className="w-30 h-18 bg-gray-200 hover:bg-blue-500 transform hover:scale-105 transition duration-300 ease-in-out flex items-center justify-center font-semibold text-gray-800 hover:text-white rounded-lg shadow-md hover:shadow-lg">
         Stories
      </div>
        </div>
        <div className='container mx-auto px-2 py-4 justify-center ' >
        <div className="w-30 h-18 bg-gray-200 hover:bg-blue-500 transform hover:scale-105 transition duration-300 ease-in-out flex items-center justify-center font-semibold text-gray-800 hover:text-white rounded-lg shadow-md hover:shadow-lg">
        Articles
      </div>
        </div>
        <div className='container mx-auto px-2 py-4 justify-center ' >
        <div className="w-30 h-18 bg-gray-200 hover:bg-blue-500 transform hover:scale-105 transition duration-300 ease-in-out flex items-center justify-center font-semibold text-gray-800 hover:text-white rounded-lg shadow-md hover:shadow-lg">
        Updates
      </div>
        </div>
        <div className='container mx-auto px-2 py-4 justify-center ' >
        <div className="w-30 h-18 bg-gray-200 hover:bg-blue-500 transform hover:scale-105 transition duration-300 ease-in-out flex items-center justify-center font-semibold text-gray-800 hover:text-white rounded-lg shadow-md hover:shadow-lg">
        Migrations
      </div>
        </div>
        
         
        
         </div>
      <div>  <Search  onSearch={handleSearch} /> </div>
    </div>
      <h1 className="text-4xl font-bold mb-8"> Our Posts </h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-8">
        {posts.map(post => (
          <div key={post.id} className="bg-white rounded-lg shadow-md overflow-hidden mb-8 hover:shadow-xl transition duration-300 relative">
            <div className="relative">
              <img src={post.image} alt={post.title} className="w-full h-48 object-cover sm:h-64 md:h-72 lg:h-80 transform hover:scale-105 transition duration-300" />
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 bg-white px-4 py-2 rounded shadow-md opacity-0 hover:opacity-100 transition duration-300">
                <p className="text-gray-700 font-semibold">Read more</p>
              </div>
              <div className="absolute inset-0 bg-gray-800 opacity-0 hover:opacity-50 flex items-center justify-center">
                <p className="text-white text-lg font-bold text-center">Read more</p>
              </div>
            </div>
            <div className="container mx-auto px-2 py-4 flex justify-start">
      <div className="w-40 h-18 bg-gray-200 hover:bg-blue-500 transform hover:scale-105 transition duration-300 ease-in-out flex items-center justify-center text-lg font-bold text-gray-800 hover:text-white rounded-lg shadow-md hover:shadow-lg">
        Hover Me!
      </div>
    </div>
            <div className="p-6">
              <h2 className="text-xl md:text-2xl font-bold mb-2">{post.title}</h2>
              <p className="text-gray-700 mb-4">{post.summary}</p>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <img src={post.author.image} alt={post.author.name} className="w-8 h-8 rounded-full mr-2" />
                  <h4 className="mt-1">{post.author.name}</h4>
                </div>
                <div className="text-right">{post.date}</div>
              </div>
               
            </div>
          </div>
        ))}
      </div>
    </div>

    <div className='container mx-auto px-4 py-8 ' >
      <h1> Latest </h1>
      <div className='grid  grid-cols-1  md:grid-cols-2  mt-6 gap-4 ' >
         
         {
                 
                 blogs.map(blog =>(

                  <div key={blog.id} className='bg-white rounded-lg shadow-md overflow-hidden mb-8 hover:shadow-xl transition duration-300 relative' >

                             <div className=' h-40 '>
                              <h1 className='text-xl  mt-4 ml-4  md:text-2xl font-bold mb-2' > {blog.head} </h1>
                              <div className='grid  grid-cols-3 ml-4 mt-6 ' >
                                           <div> 
                                            
                                            <img src={blog.author.image} alt={blog.author.name}  className='w-8 h-8 rounded-full mr-2'   />

                                             </div>
                                           <div> {blog.author.name}  </div>
                                           <div> {blog.date} </div>
                                </div>

                              </div>


                    </div> 


                 ))

         }
          



          
      </div>
    </div>

    {/*  Button Feature for loading more contents  */}
               <div className='mx-auto px-4 py-8 justify-center flex ' >
                <button className='bg-gray-400 text-black font-semibold py-2 px-4 rounded-md shadow-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-opacity-75 transition duration-300 ease-in-out transform hover:scale-105' >
                      Load More
                </button>
               </div>
    </>
  );
};

export default Blog;
