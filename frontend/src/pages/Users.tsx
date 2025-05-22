// // Deprecated. Needs to be updated to MUI.
//
// import React, { useEffect, useState, createContext, useContext } from "react";
//
//
// interface User {
//   first_name: string;
//   last_name: string;
// }
//
// const UsersContext = createContext({
//   users: [], fetchUsers: () => {}
// })
//
// export default function Users() {
//   const [users, setUsers] = useState([])
//   const fetchUsers = async () => {
//     const response = await fetch("http://localhost:8000/users")
//     const users = await response.json()
//     setUsers(users.data)
//   }
//   useEffect(() => {
//     fetchUsers()
//   }, [])
//
//   return (
//     <UsersContext.Provider value={{users, fetchUsers}}>
//       <Container maxW="container.xl" pt="100px">
//         <Stack gap={0}>
//           {users.map((user: User) => (
//             <b key={user.first_name}>{user.first_name} {user.last_name}</b>
//           ))}
//         </Stack>
//       </Container>
//     </UsersContext.Provider>
//   )
// }
