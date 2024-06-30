 import React from "react";
 

 

const PostCard = ({post}) => {

return(

    <>

        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8  " >

                    <img src={post.image} alt={post.title} className="w-full h-48 object-cover sm:h-64 md:h-72 lg:h-80 "   />

                    <div className="p-6" >

                                    <h2 className="text-xl md:text-2xl font-bold mb-2 " >  {post.title} </h2>
                                    <p className="text-gray-700 mb-4 " > {post.summary} </p>

                                    <button href={`/post/${post.id} `}  >
                                     
                                     <a className="hover:underline text-blue-600" > Read More </a>
                                    
                                    </button>


                    </div>


        </div>



    </>
)


}

export default PostCard