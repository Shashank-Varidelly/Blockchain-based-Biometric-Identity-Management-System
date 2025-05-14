pragma solidity ^0.8.0;

contract FaceRegistry {
    struct User {
        string name;
        uint256 age;
        string gender;
        string fileHash; // Hash of the stored file for reference
        string faceHash; // Face embedding hash
    }

    mapping(string => User) public users; // faceHash => User

    function register(
        string memory name,
        uint256 age,
        string memory gender,
        string memory fileHash,
        string memory faceHash
    ) public {
        require(bytes(users[faceHash].name).length == 0, "User already registered");
        users[faceHash] = User(name, age, gender, fileHash, faceHash);
    }

    function authenticate(string memory faceHash) public view returns (
        string memory name,
        uint256 age,
        string memory gender,
        string memory fileHash,
        bool success
    ) {
        User memory user = users[faceHash];
        if (bytes(user.name).length > 0) {
            return (user.name, user.age, user.gender, user.fileHash, true);
        }
        return ("", 0, "", "", false);
    }
}