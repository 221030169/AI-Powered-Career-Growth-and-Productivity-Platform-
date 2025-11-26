const User = require("../models/user");
const bcrypt = require('bcrypt');

const UsersController = {
  Create: async (req, res) => {
    try {
      console.log("Create user request:", { email: req.body.email, firstName: req.body.firstName, lastName: req.body.lastName });

      if (!req.body.password || req.body.password.trim() === '') {
        console.log("Error: Password is required");
        res.status(400).json({ message: 'Password is required' });
        return;
      }

      if (!req.body.email || req.body.email.trim() === '') {
        console.log("Error: Email is required");
        res.status(400).json({ message: 'Email is required' });
        return;
      }

      if (!req.body.firstName || req.body.firstName.trim() === '') {
        console.log("Error: First name is required");
        res.status(400).json({ message: 'First name is required' });
        return;
      }

      if (!req.body.lastName || req.body.lastName.trim() === '') {
        console.log("Error: Last name is required");
        res.status(400).json({ message: 'Last name is required' });
        return;
      }

      const hashedPassword = await bcrypt.hash(req.body.password, 10)
      const user = new User({firstName: req.body.firstName, lastName: req.body.lastName, email: req.body.email, password: hashedPassword });
      user.save((err) => {
        if (err) {
          console.log("Error saving user:", err.message);
          res.status(400).json({message: err.message || 'Bad request'})
        } else {
          console.log("User created successfully:", user.email);
          res.status(201).json({ message: 'OK' });
        }
      });
    } catch (error) {
      console.error("Unexpected error in Create user:", error);
      res.status(500).json({message: 'Internal Server Error'});
    }
  },

  Index: (req, res) => {
    User.findById(req.user_id, (err, data) => {
      if (err) {
        res.status(400).json({message: 'Unable to find user'})
      } else {
        const token = TokenGenerator.jsonwebtoken(req.user_id)
        res.status(200).json({user: data, token: token});
      }
    })
  },

  Update: async (req, res) => {
    try {
      const user = await User.findById(req.params.userId);

      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }

      user.firstName = req.body.firstName;
      user.lastName = req.body.lastName;
      user.email = req.body.email;
      await user.save();

      res.status(201).json({ message: "OK", user });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: "Internal Server Error" });
    }
  },
};

module.exports = UsersController;
