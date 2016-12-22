package com.bah.heimdall.common

import org.apache.commons.codec.binary.Base64


object CodecUtils {
  def decodeBase64(value:String): String ={
    new String (Base64.decodeBase64(value))
  }
}
