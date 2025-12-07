const User = require("../models/user");
const TokenGenerator = require("../models/token_generator")
const bcrypt = require('bcrypt')

const SessionsController = {

  Create: async (req, res) => {
    try {
      console.log("Login attempt with email:", req.body.email);
      const email = req.body.email;
      const password = req.body.password;

      let user = await User.findOne({ email: email })
      if (!user) {
        console.log("auth error: user not found for email:", email)
        res.status(404).json({ message: "auth error" });
      } else if (!(await bcrypt.compare(password, user.password))) {
        console.log("auth error: passwords do not match for user:", email)
        res.status(401).json({ message: "auth error" });
      } else {
        const token = await TokenGenerator.jsonwebtoken(user.id)
        console.log("Login successful for user:", email, "user_id:", user.id);
        res.status(201).json({ token: token, message: "OK", user_id: user.id });
      }
    } catch (error) {
      console.error("Login error:", error);
      res.status(500).json({ message: "Internal Server Error" });
    }
  }
};

module.exports = SessionsController;
